# TrendCatcher: Platform Architecture Design Document

## 1. Executive Summary & Value Proposition
TrendCatcher is an automated "early warning system" for viral consumer products. It systematically scans social media signals (TikTok, Pinterest, Reddit) to identify emerging products before they reach mainstream saturation, then automatically drafts affiliate-optimized content to capture high-intent search traffic.

This document outlines the technical architecture of the TrendCatcher platform, encompassing data ingestion, AI-driven trend scoring and analysis, automated content generation, database schema, and the user dashboard interface.

---

## 2. High-Level System Architecture

The system is designed with a **modular micro-services / layered architecture** to ensure reliability, ease of adding new social platforms, and clear separation of concerns.

```
                  +-------------------------------------------------+
                  |                 Data Sources                    |
                  |     (TikTok API/Scraper, Pinterest, Reddit)      |
                  +-----------------------+-------------------------+
                                          |
                                          v
                  +-----------------------+-------------------------+
                  |         Data Ingestion & Normalization          |
                  |   (Asynchronous workers, proxy rotation, queues) |
                  +-----------------------+-------------------------+
                                          |
                                          v
                  +-----------------------+-------------------------+
                  |              AI & Analytics Engine              |
                  |     (Trend Scoring, Sentiment, LLM parsing)     |
                  +-----------------------+-------------------------+
                                          |
                                          v
                  +-----------------------+-------------------------+
                  |               Core Database (SQLite/Turso)      |
                  |       (Products, Trends, Signals, Content)      |
                  +------------+------------------------+-----------+
                               |                        |
                               v                        v
+------------------------------+---------+   +----------+---------------------------+
|          SaaS Dashboard REST API       |   |      Automated Content Generator     |
|              (FastAPI Backend)         |   |  (LLM Article & Social Script Writer)|
+------------------------------+---------+   +----------+---------------------------+
                               |                        |
                               v                        v
+------------------------------+---------+   +----------+---------------------------+
|         SaaS Frontend Dashboard        |   |   Niche Affiliate Site Publisher     |
|        (React + Tailwind Frontend)     |   |   (Headless WordPress / Static Site) |
+----------------------------------------+   +--------------------------------------+
```

---

## 3. Core Architectural Components

### 3.1. Data Ingestion Layer (Scrapers & APIs)
The Ingestion Layer is responsible for gathering raw metrics and posts from social networks.

*   **TikTok Source:**
    *   *Data Collected:* Video URLs, captions, hashtags (e.g., `#tiktokmademebuyit`, `#amazonfinds`), views, likes, comments, shares, music/sound IDs.
    *   *Implementation:* Combined official TikTok Research API (where available) and resilient scraping modules (Playwright/Scrapy) featuring proxy rotation (residential proxies) and user-agent spoofing to avoid IP bans.
*   **Pinterest Source:**
    *   *Data Collected:* Pin descriptions, image URLs, repins, comment counts, Pinterest Trends API data.
    *   *Implementation:* Pinterest Developer API integrated with scrapers searching for shopping-related boards and emerging visual search trends.
*   **Reddit Source:**
    *   *Data Collected:* Subreddit posts (from r/shutupandtakemymoney, r/amazonfinds, r/mildlyinteresting, etc.), upvote ratio, comment count, raw comments.
    *   *Implementation:* Official Reddit API (PRAW library) to efficiently fetch hot/rising threads.

*Reliability Measures:*
*   **Proxy Rotation & Rate Limiting:** Built-in sleep backoffs and rotating residential IP pools.
*   **Asynchronous Processing:** Powered by Python's `asyncio` to fetch data concurrently without blocking execution.

---

### 3.2. AI & Trend Scoring Engine
The raw ingested data must be parsed, cleaned, and evaluated to find true early-stage trends.

#### Trend Scoring Algorithm
A product's **Velocity Score ($V$)** is calculated using multi-platform metrics weighted by relevance:

$$V = w_{tk} \cdot \Delta Tk + w_{pn} \cdot \Delta Pn + w_{rd} \cdot \Delta Rd$$

Where:
*   $\Delta Tk, \Delta Pn, \Delta Rd$ represent the growth rate of engagement metrics (likes, views, pins, upvotes, comment velocity) on TikTok, Pinterest, and Reddit over a rolling 24h, 72h, and 7-day window.
*   $w_{tk}, w_{pn}, w_{rd}$ are weights optimized for each platform ($w_{tk} = 0.5$, $w_{pn} = 0.3$, $w_{rd} = 0.2$ based on viral product generation history).

#### AI Parsing and Entity Extraction
Once a high-velocity signal is detected:
1.  **Entity Extraction (LLM):** Pass post titles/captions and top comments to an LLM (e.g., Gemini / Claude) to extract:
    *   *Product Name* (or generic descriptive name).
    *   *Key Features & Value Proposition*.
    *   *Estimated Price & Target Audience*.
2.  **Purchase Intent Analysis (NLP):** Evaluate comment sentiment. Standard sentiment tools fail here; we use LLM zero-shot classification to detect "Purchase Intent Ratio" ($PIR$):
    $$PIR = \frac{\text{Comments showing intent ("where is link?", "ordered!", "need this")}}{\text{Total comments analyzed}}$$
    Products with high $V$ and high $PIR$ are flagged as **Primary Viral Threats** (Early Warnings).

---

### 3.3. Automated Content Generation System
For verified trends, the system automatically creates high-conversion affiliate assets.

1.  **AI Copywriter Engine:**
    *   Uses custom-crafted system instructions to generate:
        *   **Long-form Affiliate Articles:** Incorporating SEO-optimized structures (Introduction, Pros/Cons, Detailed Features, Buying Guide, Comparison Tables, FAQ).
        *   **TikTok/Reels Script Ideas:** Hook, body, call-to-action, with visual cues.
        *   **Social Ads & Pinterest Pins Copy:** Short, catchy, and high CTR.
2.  **SEO Optimization Pipeline:**
    *   Pulls current search keywords related to the product.
    *   Structures the article with semantic HTML headings (`H1`, `H2`, `H3`), tables, and FAQ schemas.
3.  **Affiliate Link Integration:**
    *   Automatically searches for matching product listings on Amazon Associate, ShareASale, or CJ Affiliate to generate recommended affiliate links.

---

### 3.4. Database Schema (SQLite / Turso)
We use a relational database structure optimized for tracking product trends and historical data.

```sql
-- Track identified products
CREATE TABLE products (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    estimated_price REAL,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Raw signals collected from social platforms
CREATE TABLE social_signals (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    platform TEXT NOT NULL, -- 'tiktok', 'pinterest', 'reddit'
    external_id TEXT NOT NULL, -- Original post/video/pin ID
    post_url TEXT NOT NULL,
    engagement_score INTEGER NOT NULL, -- Normalized metric
    comment_count INTEGER DEFAULT 0,
    velocity_score REAL DEFAULT 0.0,
    raw_data TEXT, -- JSON payload of the raw signal
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Aggregated trends with velocity scores
CREATE TABLE trends (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    velocity_score REAL NOT NULL,
    purchase_intent_ratio REAL DEFAULT 0.0,
    status TEXT NOT NULL, -- 'emerging', 'viral', 'saturated'
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Generated content pieces for affiliate sites
CREATE TABLE generated_content (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    content_type TEXT NOT NULL, -- 'blog_post', 'video_script', 'social_ad'
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    seo_keywords TEXT,
    affiliate_links TEXT, -- JSON mapping of retailer to link
    status TEXT NOT NULL, -- 'draft', 'published'
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- SaaS platform subscribers/users
CREATE TABLE subscribers (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    subscription_tier TEXT DEFAULT 'free', -- 'free', 'pro', 'enterprise'
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. Technology Stack Selection

### 4.1. Backend Framework: FastAPI (Python)
*   *Why:* Lightweight, standard-compliant (`OpenAPI` automatically generated), built-in async support which is crucial for intensive IO-bound tasks like scraping and calling AI APIs. Extremely low memory footprint.

### 4.2. Frontend Framework: React (Vite) + Tailwind CSS
*   *Why:* Vite builds are highly optimized and use minimal RAM. React allows us to build a rich, interactive trend explorer dashboard. Tailwind CSS ensures rapid, clean UI development.

### 4.3. Execution Environment & Deployment (Port 3000)
*   *Requirement:* Single origin server on port `3000`.
*   *Architecture:* The FastAPI backend serves the React production build (`dist/` folder) as static files.
    *   API routes are served under `/api/*`.
    *   All other routes fall back to serving `index.html` (for React Router support).
    *   This eliminates CORS issues and keeps memory/port footprint to a single lightweight service.

---

## 5. Security & Scaling Considerations

1.  **Secure API Keys:** Database credentials, AI API keys, and proxy passwords will be stored in environment variables (`.env`) and never committed to version control.
2.  **Scraper Resilience:** Since social sites aggressively update, scrapers will use decoupled parsers. If TikTok updates its page structure, only the TikTok ingestion parser needs to be modified, leaving the scoring and generation layers unaffected.
3.  **Memory Management:** The system will utilize streaming endpoints for large AI content generations and paginate all dashboard queries to stay within resource limits.

---

## 6. Next Steps & Development Plan

1.  **Phase 1: Project Initialization (Current)**
    *   Setup Python backend skeleton with FastAPI.
    *   Setup React frontend skeleton with Vite + Tailwind CSS.
    *   Establish database sync and migration structures.
2.  **Phase 2: Ingestion & Analysis Implementation**
    *   Develop the scraper/API connectors for TikTok, Pinterest, and Reddit.
    *   Implement the scoring engine and AI entity extraction pipelines.
3.  **Phase 3: Automated Content & SaaS Dashboard**
    *   Build the AI copywriting pipeline.
    *   Implement the frontend dashboard interface for Trend Catcher SaaS subscribers.
    *   Perform rigorous end-to-end integration testing.
