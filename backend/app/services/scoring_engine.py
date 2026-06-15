import logging
from typing import Dict, Any, List, Optional

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TrendScoringEngine")

class TrendScoringEngine:
    @staticmethod
    def calculate_composite_virality_score(
        tiktok_score: float,
        instagram_score: float,
        pinterest_score: float,
        reddit_score: float
    ) -> Dict[str, Any]:
        """
        Calculates the global Composite Virality Score (CVS) using the updated 
        multi-platform weighted detection matrix defined in the signals research:
        
        CVS = (TikTok * 0.25) + (Reddit * 0.20) + (Pinterest * 0.20) + (Instagram * 0.35)
        
        Weights prioritize high purchase intent conversion platforms (Instagram & TikTok)
        validated against discovery vectors (Pinterest & Reddit).
        """
        # Ensure scores are within standard bounds [1.0, 10.0]
        tk = max(1.0, min(10.0, tiktok_score))
        ig = max(1.0, min(10.0, instagram_score))
        pin = max(1.0, min(10.0, pinterest_score))
        rd = max(1.0, min(10.0, reddit_score))

        # Weighted CVS sum
        cvs = (tk * 0.25) + (rd * 0.20) + (pin * 0.20) + (ig * 0.35)
        cvs = round(cvs, 2)

        # Classification and standard action triggers
        if cvs >= 8.0:
            status = "Viral"
            saas_class = "Saturated / Viral"
            action_trigger = "Full automation trigger; write SEO article; push social pin; syndicate script."
        elif cvs >= 6.0:
            status = "Viral" # Map to schemas.Trend status
            saas_class = "Trending / Confirmed"
            action_trigger = "Publish affiliate review content; active SEO indexing; monitor social boards."
        elif cvs >= 4.0:
            status = "emerging"
            saas_class = "Emerging Trend / Validating"
            action_trigger = "Draft copywriting assets; queue affiliate link injections; check daily trends."
        elif cvs >= 2.0:
            status = "emerging"
            saas_class = "Speculative / Monitor"
            action_trigger = "Add product to subscriber watchlist; query signals hourly."
        else:
            status = "saturated"
            saas_class = "Noise"
            action_trigger = "Filter signal out; no current commercial potential."

        return {
            "composite_virality_score": cvs,
            "status": status,
            "classification": saas_class,
            "recommended_action": action_trigger,
            "components": {
                "tiktok_weight": 0.25,
                "tiktok_score": tk,
                "instagram_weight": 0.35,
                "instagram_score": ig,
                "pinterest_weight": 0.20,
                "pinterest_score": pin,
                "reddit_weight": 0.20,
                "reddit_score": rd
            }
        }

    @classmethod
    def rank_trends(cls, products_metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ranks a list of products by calculating their CVS dynamically.
        Expects a dict for each product with keys: 'id', 'name', and individual platform scores.
        """
        ranked_list = []
        for p in products_metrics:
            # Safely fetch scores with baseline fallback of 1.0 (No signal)
            tk_score = p.get("tiktok_score", 1.0)
            ig_score = p.get("instagram_score", 1.0)
            pin_score = p.get("pinterest_score", 1.0)
            rd_score = p.get("reddit_score", 1.0)

            analysis = cls.calculate_composite_virality_score(
                tiktok_score=tk_score,
                instagram_score=ig_score,
                pinterest_score=pin_score,
                reddit_score=rd_score
            )

            ranked_list.append({
                "product_id": p.get("id"),
                "product_name": p.get("name"),
                "cvs_analysis": analysis
            })

        # Sort descending by CVS
        ranked_list.sort(key=lambda x: x["cvs_analysis"]["composite_virality_score"], reverse=True)
        return ranked_list
