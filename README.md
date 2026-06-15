# TrendCatcher

TrendCatcher is an automated "early warning system" for viral consumer products. By parsing real-time social signals across TikTok, Pinterest, and Reddit, the platform flags high-velocity trending products before they hit mainstream popularity. It then leverages LLMs to automatically generate affiliate-optimized reviews and content to capture organic search traffic and monetize via affiliate channels.

---

## Repository Structure

```text
trendcatcher/
├── backend/            # FastAPI Python backend (Ingestion, Scoring, AI Content Generator)
├── docs/               # Platform Architecture Design, schemas, and specifications
│   └── architecture.md # Detailed architecture specifications
├── frontend/           # React + Vite + Tailwind CSS dashboard UI
├── .gitignore          # Git exclusion lists for Python and Node/React dependencies
└── README.md           # This project overview and setup manual
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- Standard build tools

---

### Backend Setup

The backend is built with **FastAPI** to ensure speed, automatic OpenAPI generation, and native asynchronous execution for the scraper queue.

1.  **Navigate to backend:**
    ```bash
    cd backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install requirements:**
    ```bash
    pip install --upgrade pip
    pip install fastapi uvicorn pydantic requests motor httpx sqlalchemy
    ```

4.  **Run Development Server:**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```
    *Open [http://localhost:8000/docs](http://localhost:8000/docs) to view the interactive API swagger page.*

---

### Frontend Setup

The frontend is built with **React (Vite)** and **Tailwind CSS** for a highly responsive and responsive SaaS dashboard experience.

1.  **Navigate to frontend:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Run Development Server:**
    ```bash
    npm run dev
    ```

---

## Production Deployment (Single-Origin Server on Port 3000)

Following the platform guidelines, the entire application is bundled into a single-origin build running on port **3000** bound to all interfaces (`0.0.0.0`).

1.  **Build the Frontend:**
    ```bash
    cd frontend
    npm run build
    ```
    This generates a production-ready `dist/` folder containing static assets.

2.  **Serve Static Frontend from FastAPI Backend:**
    The FastAPI application is configured to mount the `frontend/dist` directory as static files and serve `index.html` for any unmatched SPA routes.

3.  **Launch Production Server:**
    ```bash
    # Run in background surviving terminal exit
    cd backend
    nohup uvicorn main:app --host 0.0.0.0 --port 3000 > /tmp/trendcatcher.log 2>&1 &
    ```

---

## Core Platform Workflows

1.  **Data Ingestion:** Asynchronous fetchers querying Reddit (via PRAW), Pinterest search boards, and TikTok hashtag trend lines.
2.  **AI Analysis Engine:** Scopes comments and metadata to find products with a high **Velocity Score** and high **Purchase Intent Ratio (PIR)**.
3.  **Content Generator:** Deep AI copywriter drafts long-form reviews and social scripts, injecting merchant affiliate links dynamically.
4.  **SaaS Dashboard:** Allows subscriber tracking of early trends, editing drafts, and publishing to automated affiliate blogs.
