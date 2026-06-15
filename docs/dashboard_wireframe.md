# SaaS Dashboard Wireframe & Layout Specification

This document details the interface architecture, UI components, user flow, and interaction model for the TrendCatcher SaaS dashboard mockup.

---

## 1. High-Level Wireframe Layout (ASCII Diagram)

```text
+--------------------------------------------------------------------------------------------------+
|                                           TRENDCATCHER                                           |
+---------------------+----------------------------------------------------------------------------+
|  [TC] TrendCatcher  |  [ Search products, hashtags, subreddits... ]   (Bell)  [ John Doe (PRO) ] |
+---------------------+----------------------------------------------------------------------------+
|  (o) Dashboard      |  WELCOME BACK, JOHN!                                  Sat, Jun 13, 2026    |
|                     |  +-------------------+-------------------+------------------+---------------+
|  (/) Trend Explorer |  | Active Warnings:  | Avg Velocity:     | Avg Sentiment:   | Content CTR:  |
|                     |  |  14               |  87.2%            |  84% Buy Intent  |  4.8%         |
|  [x] AI Copywriter  |  +-------------------+-------------------+------------------+---------------+
|                     |                                                                            |
|  (<) Site Publisher |  +---------------------------------------+ +-------------------------------+
|                     |  | EMERGING VIRAL PRODUCTS (LIVE BOARD)  | | PRODUCT WORKSPACE & AI ENGINE |
|  [*] Settings       |  +---------------------------------------+ +-------------------------------+
|                     |  | Product Name    Platform   Vel.  PIR  | | [ Tabs: Signals | Copywriter ]|
|                     |  | +-------------+ +--------+ +---+ +---+| |                               |
|                     |  | | RGB Cloud   | | [T][P] | | 94%| |88%|| | Selected: Smart RGB Cloud Pin |
|                     |  | +-------------+ +--------+ +---+ +---+| |                               |
|                     |  | | Jellyfish   | | [T]    | | 88%| |72%|| | Extracted Features:           |
|                     |  | +-------------+ +--------+ +---+ +---+| | * 16M Colors, App Controlled  |
|                     |  | | Levitating  | | [R]    | | 74%| |91%|| | * Dynamic sound reactivity    |
|                     |  | +-------------+ +--------+ +---+ +---+| |                               |
|                     |  | | Flex-Brush  | | [P][R] | | 61%| |65%|| | [Draft Affiliate Article v]   |
|                     |  | +-------------+ +--------+ +---+ +---+| | +---------------------------+ |
|                     |  +---------------------------------------+ | | ## The Ultimate Cloud Pin.. | |
|                     |                                            | | *Are you tired of boring..*| |
|                     |                                            | +---------------------------+ |
|                     |                                            | [ Copy Draft ] [ Sync Site ]  |
|                     |                                            +-------------------------------+
+---------------------+--------------------------------------------+-------------------------------+
```

---

## 2. Dashboard Sections & Component Specifications

The dashboard UI is divided into three primary regions: Sidebar, Header, and Main Content Canvas.

### 2.1. Navigation Sidebar (Left Panel)
*   **Logo Brand Area:** Sleek typography of `TrendCatcher` with an abstract wave/signal icon.
*   **Dashboard (Default View):** Focuses on current active viral trends, quick analytics, and instant content generation.
*   **Trend Explorer:** Advanced grid view with sorting, search, filtering by niche (Tech, Home, Fashion), and social channel filter toggles (TikTok, Pinterest, Reddit).
*   **AI Copywriter Workspace:** Dedicated interface for fine-tuning system copy, managing tone of voice, selecting keyword catalogs, and templates.
*   **Sync & Publishing Config:** Settings panel to connect headless WordPress sites, Shopify stores, and Medium blogs for auto-publication.
*   **User Account Widget:** Displays subscriber profile, subscription tier indicator (`PRO` / `ENTERPRISE`), and simple subscription billing info.

### 2.2. Global Navigation Header (Top Bar)
*   **Global Search Input:** Predictive typing search that filters products, hashtags, subreddits, or active content pieces.
*   **Notifications Bell:** Triggers dropdown preview of fresh "Early Warning" signals (e.g., *“ALERT: #LevitatingPlantPot views surged +140% in last 12h on TikTok”*).
*   **Quick Scan Trigger:** CTA button forcing immediate background execution of scrapers on specified terms.

### 2.3. Key Metric Cards (Row 1)
*   **Active Early Warnings:** Number of products currently flagged as "Emerging" (Velocity > 70%, PIR > 60%, and not yet saturated).
*   **Average Trend Velocity:** Mean velocity index across all active tracked items.
*   **Buy Intent Sentiment (Average PIR):** Overall percentage of buyer intent sentiment from monitored platform comments.
*   **Affiliate Content Click-Through Rate (CTR):** Standard success metric representing clicks/actions on published automated pages.

---

## 3. Product Workspace & Core Interactive Panels (Grid Layout)

The core workflow revolves around selecting an emerging product on the left and completing its conversion in the workspace on the right.

### 3.1. Left Column: Emerging Viral Products Board
*   **Layout:** A rich data list/table showing high-intent products.
*   **Key Columns:**
    *   *Product Name & Meta:* Dynamic image thumbnail, brand, and target consumer category.
    *   *Social Signals Indicator:* Badges highlighting platforms of origin (TikTok, Pinterest, Reddit) showing individual engagement multipliers.
    *   *Velocity Score:* Interactive progress bar color-coded by trend status:
        *   **Emerging (Green, Score >70%):** Best time to create content. High growth, low saturation.
        *   **Viral (Orange, Score >85%):** Saturated, but high search volume. Capture remaining traffic.
        *   **Saturated (Red, Score >95%):** Peak phase. Traffic fading, competition high.
    *   *PIR (Purchase Intent Ratio):* Indicates the portion of comment interactions asking where to buy, order status, or pricing.
    *   *Action CTA:* Clicking an item highlights and populates the right workspace.

### 3.2. Right Column: Product Detail & AI Content Workspace (Tabbed Interface)

#### Tab A: Viral Signals Analytics
*   **Trend Velocity Chart:** Displays a line chart outlining view count / repin growth over a rolling 7-day period. This visually proves the product is in its exponential upward phase.
*   **Purchase Intent Sentiment Quotes:** A curated list of direct comments highlighting strong purchasing desire.
*   **Extracted Entities / Key Features:** Bulleted list generated by the AI parser summarizing what features make the product stand out.

#### Tab B: AI Content Copywriter
*   **Copywriter Type Selector:** Button toggles for:
    1.  *Long-form SEO Blog Review* (Optimized with heading schemas and FAQs).
    2.  *TikTok Video Script* (Timecoded cues, hooks, visual suggestions).
    3.  *Social Media Pins/Ads Copy* (Short, punchy, click-focused).
*   **Dynamic Editor Area:** A rich text interface populated with the AI draft. Users can live-edit, adjust the keywords pool, and preview structure.
*   **Action Row:**
    *   `Generate New Draft` button to cycle LLM seeds.
    *   `Insert Affiliate Links` matching high-performing retailer offers (Amazon, ShareASale).
    *   `Copy to Clipboard` for manual entry.
    *   `Sync & Publish` button to push the live post straight to connected affiliate channels.

---

## 4. User Interaction & Data Flow

```text
+-------------------+      (Selects Item)      +-----------------------------+
| Emerging Products | -----------------------> | Workspace Populates Details |
+-------------------+                          +--------------+--------------+
                                                              |
                                                    (Clicks Content Tab)
                                                              v
+-------------------+      (Click Publish)     +-----------------------------+
| Affiliate Site    | <----------------------- | AI Copywriter Workspace     |
| (Niche Blog) Live |                          | Drafts Review & Social Ads  |
+-------------------+                          +-----------------------------+
```

1.  **Discovery:** The system's background crawlers identify a surge in Reddit views and TikTok likes for " Levitating Smart Plant Pot".
2.  **Notification:** The user gets a header alert and the product appears on top of the "Emerging Products" list with a Velocity of **94%** and a PIR of **88%**.
3.  **Analysis:** The user clicks the product. The workspace reveals a skyrocketing 7-day trajectory chart and a summary of top comments.
4.  **Generation:** The user selects the "AI Copywriter" tab, picks "SEO Blog Review", and clicks "Generate". The workspace immediately fills with a draft review formatted in Markdown.
5.  **Monetization:** The user inserts Amazon affiliate codes and clicks "Publish". The article is instantly live on their niche automated blog.
