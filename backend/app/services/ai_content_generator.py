import os
import re
import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from app.core.config import settings

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AIContentGenerator")

class AIContentGenerator:
    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.claude_key = settings.CLAUDE_API_KEY or os.getenv("CLAUDE_API_KEY", "")

    async def generate_affiliate_assets(
        self,
        product_name: str,
        category: str,
        features: List[str],
        estimated_price: float,
        cvs_score: float,
        pir_score: float,
        affiliate_tracking_id: str = "trendcatcher-20"
    ) -> Dict[str, Any]:
        """
        Generates highly optimized, ready-to-publish affiliate marketing content assets:
        1. Blog Post Review (using prelaunch_content_strategy markdown templates)
        2. Pinterest Pin variations
        3. TikTok / Reels video script with Visual & Voice-over directives.
        """
        logger.info(f"Generating content assets for: '{product_name}'...")

        # Construct semantic prompts
        features_str = ", ".join(features)
        
        # Try Gemini LLM if key is configured
        if self.gemini_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_key}"
                prompt = f"""
                You are a senior affiliate marketer, SEO copywriter, and viral social media creator.
                Generate high-converting content assets for the following trending product:
                
                PRODUCT: {product_name}
                CATEGORY: {category}
                FEATURES: {features_str}
                PRICE: ${estimated_price:.2f}
                VIRALITY METRICS: CVS Score {cvs_score}/10, Purchase Intent Ratio {pir_score:.2%}
                AFFILIATE TRACKING ID: {affiliate_tracking_id}
                
                Generate a JSON response containing exactly:
                1. "blog_post": Markdown blog post following the 'Trending Now Product Spotlight' format. Must include:
                   - Captivating hook title and intro.
                   - Product value proposition.
                   - Multi-angle feature deep dive.
                   - Structured 'Should you buy this?' verdict.
                   - Simulated affiliate link [Buy {product_name} on Amazon](https://amazon.com/dp/B0000000/?tag={affiliate_tracking_id})
                2. "pinterest_pins": A list of 3 distinct Pin assets (each with a vertical Pin Title, Description, and Visual Design Suggestion).
                3. "video_script": A highly viral TikTok/Reels short-form script containing:
                   - Hook variations (e.g. "TikTok made me buy it", "Stop scrolling if...").
                   - Visual Scene descriptions.
                   - Voice-Over (VO) audio cues.
                   - Text overlays (On-screen text).
                
                Return ONLY valid JSON in this format:
                {{
                    "blog_post": "Markdown text here...",
                    "pinterest_pins": [
                        {{"title": "Title 1", "description": "Desc 1", "visual_idea": "Visual Idea 1"}},
                        {{"title": "Title 2", "description": "Desc 2", "visual_idea": "Visual Idea 2"}},
                        {{"title": "Title 3", "description": "Desc 3", "visual_idea": "Visual Idea 3"}}
                    ],
                    "video_script": {{
                        "hooks": ["Hook 1", "Hook 2"],
                        "scenes": [
                            {{"scene_number": 1, "visuals": "Visual instructions", "audio": "Voiceover audio", "text_overlay": "On-screen text"}}
                        ]
                    }}
                }}
                """
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                async with httpx.AsyncClient() as client:
                    response = await client.post(url, json=payload, timeout=15.0)
                    if response.status_code == 200:
                        result = response.json()
                        text_response = result["candidates"][0]["content"]["parts"][0]["text"]
                        
                        # Parse JSON block
                        json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
                        if json_match:
                            data = json.loads(json_match.group(0))
                            data["generation_method"] = "gemini_llm"
                            return data
            except Exception as e:
                logger.warning(f"Gemini content generation failed: {str(e)}. Triggering semantic fallback generator.")

        # High-Fidelity Local Markdown/Copywriting Fallback
        return self._generate_rule_fallback_assets(
            product_name, category, features, estimated_price, cvs_score, pir_score, affiliate_tracking_id
        )

    def _generate_rule_fallback_assets(
        self,
        product_name: str,
        category: str,
        features: List[str],
        estimated_price: float,
        cvs_score: float,
        pir_score: float,
        affiliate_tracking_id: str
    ) -> Dict[str, Any]:
        """
        Constructs expert copywriting templates from the prelaunch_content_strategy.md blueprint.
        Ensures perfect, beautiful SEO and social copy offline.
        """
        features_li = "\n".join([f"- **{f}**: Hand-selected for premium durability." for f in features])
        amazon_link = f"https://amazon.com/dp/B01TRENDS?tag={affiliate_tracking_id}"

        # 1. Markdown Blog Post Review
        blog_post_md = f"""# 5 Trending Home Goods Going Viral on TikTok Right Now (June 2026)

*Disclosure: This post contains affiliate links. If you click through and make a purchase, we may receive a small commission at no additional cost to you.*

Social media is absolutely obsessed with aesthetic upgrades this month. From Pinterest boards to TikTok Reels, creators are showing off smart, gorgeous ways to level up daily spaces. 

Today we are spotlighting a major viral breakout that has captured a **{cvs_score}/10 Composite Virality Score** on our signals dashboard: the **{product_name}**.

---

## The Main Event: {product_name}

If you have been on r/AmazonFinds or TikTok's `#tiktokmademebuyit` tag recently, you have definitely seen this in action. With a soaring **{pir_score:.0%} purchase intent ratio**, shoppers are literally begging creators for store links in comment threads.

### Key Value Propositions & Features
{features_li}

### Pricing & Value Assessment
Coming in at around **${estimated_price:.2f}**, it offers an incredible price-to-performance ratio compared to luxury counterparts. It represents a low-cost, high-impact aesthetic asset for any home.

### The Verdict: Is It Actually Worth It?
**Yes, 100%.** If you want to transform your desk, kitchen, or room vibe with a trending mag-safe product, this is the item to buy before it inevitably sells out.

👉 [**Get Your {product_name} on Amazon Now (Check Prime Shipping)**]({amazon_link})
"""

        # 2. Pinterest Pins Variations
        pinterest_pins = [
            {
                "title": f"The Viral {product_name} Everyone Is Talking About!",
                "description": f"This aesthetic {category} find is going viral on TikTok and Pinterest! Read our honest review & find where to get it under ${estimated_price:.2f}.",
                "visual_idea": f"Vertical pin (2:3 aspect ratio). Side-by-side split screen showing {product_name} unboxed on top, and glowing user comments on the bottom. Add bold overlay text: 'TIKTOK MADE ME BUY IT!'."
            },
            {
                "title": f"Stop Scrolling! 5 Aesthetic {category} Finds You Need in 2026",
                "description": f"Level up your space with the viral {product_name}. Check out why it got a high 10/10 purchase intent score on social circles.",
                "visual_idea": f"Vertical pin (2:3 aspect ratio). Close-up of {product_name} in an elegant room setting. Minimalist fonts, earthy tones, with overlay: 'Must-Have Home Upgrades under ${estimated_price:.2f}'."
            },
            {
                "title": f"Honest Review: Is the Trending {product_name} Actually Worth It?",
                "description": f"We analyzed over 10k TikTok and Reddit comments to find if the {product_name} is worth your hard-earned money. Click for the full review!",
                "visual_idea": f"Vertical pin (2:3 aspect ratio). High-contrast thumbnail with a question mark over {product_name}. Overlay: 'GENUINE RETAIL BREAKDOWN'."
            }
        ]

        # 3. Short-form Video Scripts (TikTok/Reels)
        video_script = {
            "hooks": [
                f"I swear TikTok makes me buy the weirdest things... but this one actually blew my mind.",
                f"Stop scrolling if you want to upgrade your desk or room setup on a budget.",
                f"Here is a viral {category} find that is 100% worth your money."
            ],
            "scenes": [
                {
                    "scene_number": 1,
                    "visuals": f"Fast zoom-in on the {product_name} unboxing. Clean lighting, ASMR tapping on the product shell.",
                    "audio": "POV: You found the one viral TikTok product that is actually worth your money.",
                    "text_overlay": f"Viral {category} Gem ✨"
                },
                {
                    "scene_number": 2,
                    "visuals": f"Show the product in action. Demonstrating key features: {features[0] if features else 'Stunning aesthetic flow'}.",
                    "audio": f"It is the {product_name}. It has {features[0] if features else 'incredible features'} and looks amazing in any desk or room setup.",
                    "text_overlay": "Aesthetic + Functional 😍"
                },
                {
                    "scene_number": 3,
                    "visuals": f"Close-up of the price tag or simulated online storefront listing for ${estimated_price:.2f}.",
                    "audio": f"Best part? It is under ${estimated_price:.2f} right now on Amazon. The link is in my bio to grab yours!",
                    "text_overlay": f"Link in Bio! (${estimated_price:.2f})"
                }
            ]
        }

        return {
            "blog_post": blog_post_md,
            "pinterest_pins": pinterest_pins,
            "video_script": video_script,
            "generation_method": "expert_templates_fallback"
        }
