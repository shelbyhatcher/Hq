import asyncio
import json
import os
import sys
import unittest
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.api.endpoints import build_trend_feed  # noqa: E402
from app.core.db import Base  # noqa: E402
from app.models import db_models  # noqa: E402
from app.services.reddit_ingest import (  # noqa: E402
    RedditIngestService,
    RedditIngestionError,
    persist_verified_reddit_posts,
)


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


class FakeClient:
    def __init__(self, response):
        self.response = response
        self.requests = []

    async def get(self, url, params=None, headers=None, timeout=None):
        self.requests.append({"url": url, "params": params, "headers": headers, "timeout": timeout})
        return self.response


class RedditPublicJsonIngestTests(unittest.TestCase):
    def test_public_json_ingest_normalizes_posts_with_provenance(self):
        created_utc = (datetime.utcnow() - timedelta(hours=2)).timestamp()
        payload = {
            "kind": "Listing",
            "data": {
                "children": [
                    {
                        "kind": "t3",
                        "data": {
                            "id": "abc123",
                            "name": "t3_abc123",
                            "title": "This desk gadget is a must-have Amazon find",
                            "author": "verified_redditor",
                            "score": 420,
                            "upvote_ratio": 0.94,
                            "num_comments": 84,
                            "url": "https://example.com/product",
                            "permalink": "/r/gadgets/comments/abc123/test/",
                            "created_utc": created_utc,
                            "subreddit": "gadgets",
                            "subreddit_name_prefixed": "r/gadgets",
                            "over_18": False,
                            "is_self": False,
                            "post_hint": "link",
                            "thumbnail": "https://example.com/thumb.jpg",
                        },
                    }
                ]
            },
        }
        fake_client = FakeClient(FakeResponse(payload=payload))
        service = RedditIngestService(http_client=fake_client)

        posts = asyncio.run(service.ingest_subreddit_posts("gadgets", limit=5, sort="rising"))

        self.assertEqual(len(posts), 1)
        post = posts[0]
        self.assertEqual(post["scrape_method"], "reddit_public_json")
        self.assertEqual(post["source_platform"], "reddit")
        self.assertEqual(post["source_url"], "https://www.reddit.com/r/gadgets/comments/abc123/test/")
        self.assertEqual(post["provenance"]["ingest_method"], "reddit_public_json")
        self.assertIn("/r/gadgets/rising.json", post["provenance"]["public_json_url"])
        self.assertNotIn("simulation", json.dumps(post).lower())
        self.assertEqual(fake_client.requests[0]["params"], {"limit": 5, "raw_json": 1})

    def test_public_json_ingest_raises_without_fallback_on_http_error(self):
        fake_client = FakeClient(FakeResponse(status_code=503, payload={"error": "unavailable"}))
        service = RedditIngestService(http_client=fake_client)

        with self.assertRaises(RedditIngestionError):
            asyncio.run(service.ingest_subreddit_posts("gadgets", limit=5))

    def test_trend_feed_exposes_only_verified_reddit_public_json_rows(self):
        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        db = Session()
        try:
            # Legacy/unverified seeded row should never appear in /api/trends.
            unverified_product = db_models.Product(name="Old seeded product", description="mock", category="mock", estimated_price=9.99)
            db.add(unverified_product)
            db.flush()
            db.add(
                db_models.Trend(
                    product_id=unverified_product.id,
                    velocity_score=9.9,
                    purchase_intent_ratio=0.9,
                    status="viral",
                    access_level="public",
                )
            )
            db.commit()

            verified_post = {
                "post_id": "t3_live123",
                "reddit_id": "live123",
                "title": "This kitchen gadget is worth it",
                "author": "real_author",
                "score": 250,
                "upvote_ratio": 0.91,
                "comment_count": 50,
                "url": "https://example.com/product",
                "permalink": "https://www.reddit.com/r/INEEEEDIT/comments/live123/test/",
                "source_url": "https://www.reddit.com/r/INEEEEDIT/comments/live123/test/",
                "created_utc": (datetime.utcnow() - timedelta(hours=1)).timestamp(),
                "subreddit": "INEEEEDIT",
                "is_self": False,
                "thumbnail": None,
                "thumbnail_is_image": False,
                "scrape_method": "reddit_public_json",
                "source_platform": "reddit",
                "provenance": {
                    "source_platform": "reddit",
                    "ingest_method": "reddit_public_json",
                    "public_json_url": "https://www.reddit.com/r/INEEEEDIT/rising.json",
                    "public_json_params": {"limit": 5, "raw_json": 1},
                    "fetched_at": datetime.utcnow().isoformat(),
                    "subreddit": "INEEEEDIT",
                    "reddit_fullname": "t3_live123",
                    "permalink": "https://www.reddit.com/r/INEEEEDIT/comments/live123/test/",
                },
            }
            counts = persist_verified_reddit_posts(db, [verified_post])
            self.assertEqual(counts["written"], 1)

            feed = build_trend_feed(db, user=None, include_locked=True)
            self.assertEqual(len(feed), 1)
            self.assertEqual(feed[0]["source_platform"], "reddit")
            self.assertEqual(feed[0]["source_ingest_method"], "reddit_public_json")
            self.assertTrue(feed[0]["live_source_verified"])
            self.assertEqual(feed[0]["provenance"]["ingest_method"], "reddit_public_json")
            self.assertEqual(feed[0]["product"]["name"], "This kitchen gadget is worth it")
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
