import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

import httpx
from sqlalchemy.orm import Session

from app.models import db_models

logger = logging.getLogger("RedditIngestService")

# Product-discovery subreddits selected for public, no-auth JSON ingestion.
MONITORED_SUBREDDITS = [
    "DidntKnowIWantedThat",
    "INEEEEDIT",
    "AmazonFind",
    "TikTokMadeMeBuyIt",
    "shutupandtakemymoney",
    "gadgets",
    "HomeDecorating",
]

VALID_REDDIT_SORTS = {"hot", "new", "rising", "top"}
PRODUCT_TERMS = (
    "amazon",
    "buy",
    "bought",
    "order",
    "ordered",
    "product",
    "gadget",
    "find",
    "must-have",
    "must have",
    "need",
    "wanted",
    "worth it",
    "tiktok made me buy it",
    "favorite",
    "upgrade",
)


class RedditIngestionError(RuntimeError):
    """Raised when verified Reddit public JSON cannot be fetched or parsed."""


@dataclass
class RedditIngestResult:
    subreddit: str
    fetched_posts: int = 0
    written_trends: int = 0
    updated_trends: int = 0
    skipped_posts: int = 0
    errors: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "subreddit": self.subreddit,
            "fetched_posts": self.fetched_posts,
            "written_trends": self.written_trends,
            "updated_trends": self.updated_trends,
            "skipped_posts": self.skipped_posts,
            "errors": self.errors,
        }


def _utc_from_timestamp(timestamp: Optional[float]) -> Optional[datetime]:
    if timestamp is None:
        return None
    try:
        return datetime.utcfromtimestamp(float(timestamp))
    except (TypeError, ValueError, OSError):
        return None


def _clean_subreddit_name(subreddit_name: str) -> str:
    cleaned = subreddit_name.strip().replace("r/", "").replace("/", "")
    if not re.fullmatch(r"[A-Za-z0-9_]{2,50}", cleaned):
        raise RedditIngestionError("Invalid subreddit name for Reddit public JSON ingestion.")
    return cleaned


def _clamp_limit(limit: int, max_limit: int = 25) -> int:
    try:
        value = int(limit)
    except (TypeError, ValueError):
        return 10
    return max(1, min(value, max_limit))


def _safe_text(value: Any, max_length: int = 500) -> str:
    text = str(value or "").strip()
    return text[:max_length]


def _product_signal_score(post: Dict[str, Any]) -> float:
    """Lightweight relevance gate based only on verified Reddit metadata.

    This is not an AI extraction and does not invent a product name; it only
    prioritizes Reddit posts whose title/subreddit metadata look product-related.
    """
    title = post.get("title", "").lower()
    subreddit = post.get("subreddit", "").lower()
    score = 0.0
    if any(term in title for term in PRODUCT_TERMS):
        score += 1.0
    if subreddit in {name.lower() for name in MONITORED_SUBREDDITS}:
        score += 0.5
    if post.get("url") and not post.get("is_self"):
        score += 0.25
    return score


def build_product_from_reddit_post(post: Dict[str, Any]) -> db_models.Product:
    title = _safe_text(post.get("title"), 180) or "Verified Reddit product signal"
    subreddit = _safe_text(post.get("subreddit"), 100)
    description = (
        f"Verified Reddit public JSON signal from r/{subreddit}. "
        "TrendCatcher is showing this row because it was fetched from Reddit's public JSON endpoint "
        "with source provenance; product/entity enrichment is not yet applied. "
        f"Original title: {title}"
    )
    return db_models.Product(
        name=title,
        description=description,
        category=f"Reddit / r/{subreddit}" if subreddit else "Reddit signal",
        estimated_price=0.0,
        image_url=post.get("thumbnail") if post.get("thumbnail_is_image") else None,
    )


def calculate_reddit_velocity(post: Dict[str, Any], collected_at: Optional[datetime] = None) -> Dict[str, Any]:
    collected_at = collected_at or datetime.utcnow()
    created_at = _utc_from_timestamp(post.get("created_utc")) or collected_at
    age_hours = max((collected_at - created_at).total_seconds() / 3600.0, 1.0)
    score = max(0, int(post.get("score") or 0))
    comments = max(0, int(post.get("comment_count") or 0))
    upvotes_per_hour = score / age_hours
    comment_to_upvote_ratio = comments / score if score else 0.0

    # Map only observed Reddit public metadata onto a conservative 0-10 score.
    upvote_factor = min(10.0, (upvotes_per_hour / 150.0) * 6.0)
    discussion_factor = min(10.0, (comment_to_upvote_ratio / 0.35) * 3.0)
    relevance_factor = min(10.0, _product_signal_score(post) * 2.0)
    reddit_score = round(max(1.0, min(10.0, upvote_factor + discussion_factor + relevance_factor)), 1)

    return {
        "reddit_score": reddit_score,
        "upvotes_per_hour": round(upvotes_per_hour, 2),
        "comment_to_upvote_ratio": round(comment_to_upvote_ratio, 3),
        "age_hours": round(age_hours, 2),
        "observed_score": score,
        "observed_comment_count": comments,
        "product_signal_score": round(_product_signal_score(post), 2),
    }


def status_from_reddit_score(reddit_score: float) -> str:
    if reddit_score >= 8.0:
        return "viral"
    if reddit_score >= 4.0:
        return "emerging"
    return "watching"


class RedditIngestService:
    """Fetch verified live Reddit data from public JSON endpoints only.

    This service intentionally has no PRAW/client-secret path and no simulation
    fallback. If Reddit is blocked, rate-limited, or returns invalid data, callers
    receive RedditIngestionError and no rows should be written as live trends.
    """

    def __init__(
        self,
        http_client: Optional[httpx.AsyncClient] = None,
        base_url: str = "https://www.reddit.com",
        user_agent: str = "TrendCatcher/1.0 verified-public-json-ingest",
    ):
        self.http_client = http_client
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent

    async def ingest_subreddit_posts(
        self,
        subreddit_name: str,
        limit: int = 10,
        sort: str = "rising",
    ) -> List[Dict[str, Any]]:
        subreddit = _clean_subreddit_name(subreddit_name)
        sort_name = sort.lower().strip()
        if sort_name not in VALID_REDDIT_SORTS:
            raise RedditIngestionError(f"Unsupported Reddit sort '{sort}'.")

        safe_limit = _clamp_limit(limit)
        endpoint_path = f"/r/{subreddit}/{sort_name}.json"
        request_url = f"{self.base_url}{endpoint_path}"
        params = {"limit": safe_limit, "raw_json": 1}
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }

        fetched_at = datetime.utcnow()
        logger.info("Fetching verified Reddit public JSON: r/%s sort=%s limit=%s", subreddit, sort_name, safe_limit)

        try:
            if self.http_client is not None:
                response = await self.http_client.get(request_url, params=params, headers=headers, timeout=10.0)
            else:
                async with httpx.AsyncClient(follow_redirects=True) as client:
                    response = await client.get(request_url, params=params, headers=headers, timeout=10.0)
        except httpx.HTTPError as exc:
            raise RedditIngestionError(f"Reddit public JSON request failed for r/{subreddit}: {exc}") from exc

        if response.status_code != 200:
            raise RedditIngestionError(
                f"Reddit public JSON returned HTTP {response.status_code} for r/{subreddit}. "
                "No live trend rows were written."
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise RedditIngestionError(f"Reddit public JSON returned invalid JSON for r/{subreddit}.") from exc

        children = payload.get("data", {}).get("children") if isinstance(payload, dict) else None
        if not isinstance(children, list):
            raise RedditIngestionError(f"Reddit public JSON response for r/{subreddit} was not a listing.")

        posts: List[Dict[str, Any]] = []
        for child in children:
            if not isinstance(child, dict) or child.get("kind") != "t3":
                continue
            data = child.get("data") or {}
            if not isinstance(data, dict) or not data.get("id") or not data.get("permalink"):
                continue
            if data.get("over_18"):
                continue

            permalink = _safe_text(data.get("permalink"), 500)
            source_url = f"https://www.reddit.com{permalink}" if permalink.startswith("/") else permalink
            thumbnail = data.get("thumbnail")
            thumbnail_is_image = isinstance(thumbnail, str) and thumbnail.startswith("http")
            post_id = _safe_text(data.get("name") or f"t3_{data.get('id')}", 100)

            post = {
                "post_id": post_id,
                "reddit_id": _safe_text(data.get("id"), 100),
                "title": _safe_text(data.get("title"), 500),
                "author": _safe_text(data.get("author"), 100),
                "score": int(data.get("score") or 0),
                "upvote_ratio": float(data.get("upvote_ratio") or 0.0),
                "comment_count": int(data.get("num_comments") or 0),
                "url": _safe_text(data.get("url"), 500),
                "permalink": source_url,
                "created_utc": data.get("created_utc"),
                "subreddit": _safe_text(data.get("subreddit") or subreddit, 100),
                "subreddit_name_prefixed": _safe_text(data.get("subreddit_name_prefixed") or f"r/{subreddit}", 100),
                "is_self": bool(data.get("is_self")),
                "post_hint": _safe_text(data.get("post_hint"), 100),
                "thumbnail": thumbnail if thumbnail_is_image else None,
                "thumbnail_is_image": thumbnail_is_image,
                "scrape_method": "reddit_public_json",
                "source_platform": "reddit",
                "source_url": source_url,
                "source_endpoint": request_url,
                "source_params": params,
                "fetched_at": fetched_at.isoformat(),
                "provenance": {
                    "source_platform": "reddit",
                    "ingest_method": "reddit_public_json",
                    "public_json_url": request_url,
                    "public_json_params": params,
                    "fetched_at": fetched_at.isoformat(),
                    "subreddit": subreddit,
                    "sort": sort_name,
                    "reddit_kind": child.get("kind"),
                    "reddit_fullname": post_id,
                    "permalink": source_url,
                },
            }
            post["reddit_velocity"] = calculate_reddit_velocity(post, fetched_at)
            posts.append(post)

        return posts

    # Backward-compatible helper for older callers/tests that used the previous
    # method name. It now uses only verified public JSON and never simulates.
    async def fetch_subreddit_posts(self, subreddit_name: str, limit: int = 10, sort: str = "rising") -> List[Dict[str, Any]]:
        return await self.ingest_subreddit_posts(subreddit_name, limit=limit, sort=sort)

    def calculate_reddit_velocity(
        self,
        upvotes_3h: int,
        cross_posts_24h: int,
        comment_to_upvote_ratio: float,
    ) -> Dict[str, Any]:
        """Compatibility wrapper for previous score callers.

        This method does not fetch or fabricate data; it maps caller-provided
        observed metrics to the legacy Reddit score shape.
        """
        upvote_factor = min(10.0, (max(0, upvotes_3h) / 500) * 4.0)
        crosspost_factor = min(10.0, (max(0, cross_posts_24h) / 5) * 3.0)
        discussion_factor = min(10.0, (max(0.0, comment_to_upvote_ratio) / 0.4) * 3.0)
        reddit_score = round(max(1.0, min(10.0, upvote_factor * 0.40 + crosspost_factor * 0.30 + discussion_factor * 0.30)), 1)
        return {
            "reddit_score": reddit_score,
            "is_early_warning": {
                "upvote_velocity": upvotes_3h > 100,
                "cross_post_frequency": cross_posts_24h > 3,
                "discussion_ratio": comment_to_upvote_ratio > 0.3,
            },
            "is_viral": {
                "upvote_velocity": upvotes_3h > 1000,
                "cross_post_frequency": cross_posts_24h > 10,
                "discussion_ratio": comment_to_upvote_ratio > 0.5,
            },
            "comment_to_upvote_ratio": comment_to_upvote_ratio,
            "cross_posts_24h": cross_posts_24h,
        }


def _trend_provenance(post: Dict[str, Any], metrics: Dict[str, Any]) -> str:
    provenance = dict(post.get("provenance") or {})
    provenance["metrics"] = metrics
    provenance["observed_fields"] = {
        "score": post.get("score"),
        "upvote_ratio": post.get("upvote_ratio"),
        "comment_count": post.get("comment_count"),
        "created_utc": post.get("created_utc"),
        "title": post.get("title"),
        "author": post.get("author"),
    }
    return json.dumps(provenance, sort_keys=True)


def persist_verified_reddit_posts(
    db: Session,
    posts: Iterable[Dict[str, Any]],
    min_velocity_score: float = 1.0,
) -> Dict[str, int]:
    """Persist only posts fetched through verified Reddit public JSON.

    Any post missing explicit reddit_public_json provenance is skipped. This is
    the gate that prevents old simulated objects or hand-built rows from being
    written as live trends.
    """
    written = 0
    updated = 0
    skipped = 0
    collected_at = datetime.utcnow()

    for post in posts:
        provenance = post.get("provenance") or {}
        if (
            post.get("source_platform") != "reddit"
            or post.get("scrape_method") != "reddit_public_json"
            or provenance.get("ingest_method") != "reddit_public_json"
            or not post.get("post_id")
            or not post.get("source_url")
        ):
            skipped += 1
            continue

        metrics = post.get("reddit_velocity") or calculate_reddit_velocity(post, collected_at)
        reddit_score = float(metrics.get("reddit_score") or 0.0)
        if reddit_score < min_velocity_score:
            skipped += 1
            continue

        existing = (
            db.query(db_models.Trend)
            .filter(
                db_models.Trend.source_platform == "reddit",
                db_models.Trend.source_external_id == post["post_id"],
            )
            .first()
        )

        source_created_at = _utc_from_timestamp(post.get("created_utc"))
        if existing:
            trend = existing
            product = trend.product
            if product:
                product.name = _safe_text(post.get("title"), 180) or product.name
                product.description = build_product_from_reddit_post(post).description
                product.category = f"Reddit / r/{post.get('subreddit')}"
                product.image_url = post.get("thumbnail") if post.get("thumbnail_is_image") else None
                db.add(product)
            updated += 1
        else:
            product = build_product_from_reddit_post(post)
            db.add(product)
            db.flush()
            trend = db_models.Trend(product_id=product.id, access_level="public")
            db.add(trend)
            written += 1

        trend.velocity_score = reddit_score
        trend.purchase_intent_ratio = 0.0
        trend.status = status_from_reddit_score(reddit_score)
        trend.scanned_at = collected_at
        trend.source_platform = "reddit"
        trend.source_external_id = post["post_id"]
        trend.source_url = _safe_text(post.get("source_url"), 500)
        trend.source_subreddit = _safe_text(post.get("subreddit"), 100)
        trend.source_title = _safe_text(post.get("title"), 500)
        trend.source_author = _safe_text(post.get("author"), 100)
        trend.source_created_at = source_created_at
        trend.source_collected_at = collected_at
        trend.source_ingest_method = "reddit_public_json"
        trend.live_source_verified = True
        trend.provenance_json = _trend_provenance(post, metrics)
        db.add(trend)

    db.commit()
    return {"written": written, "updated": updated, "skipped": skipped}


async def ingest_and_persist_subreddit(
    db: Session,
    subreddit_name: str,
    limit: int = 10,
    sort: str = "rising",
    service: Optional[RedditIngestService] = None,
) -> RedditIngestResult:
    subreddit = _clean_subreddit_name(subreddit_name)
    service = service or RedditIngestService()
    posts = await service.ingest_subreddit_posts(subreddit, limit=limit, sort=sort)
    counts = persist_verified_reddit_posts(db, posts)
    return RedditIngestResult(
        subreddit=subreddit,
        fetched_posts=len(posts),
        written_trends=counts["written"],
        updated_trends=counts["updated"],
        skipped_posts=counts["skipped"],
    )
