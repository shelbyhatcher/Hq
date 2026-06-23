import os
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api import endpoints
from app.api.endpoints import seed_database
from app.core.config import settings
from app.core.db import Base, engine, SessionLocal
from app.models import db_models  # noqa: F401
from app.scheduler import run_scheduler_loop_async

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Seed database with initial products and trends
    db = SessionLocal()
    try:
        seed_database(db)
    except Exception as e:
        print(f"Error seeding database on startup: {e}")
    finally:
        db.close()
        
    # 2. Start scheduler background task (Interval configured via environment variable)
    interval = int(os.getenv("SCHEDULER_INTERVAL", "86400"))
    scheduler_task = asyncio.create_task(run_scheduler_loop_async(interval))
    
    yield
    
    # Cleanup on shutdown
    scheduler_task.cancel()
    try:
        await scheduler_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(endpoints.router, prefix=settings.API_V1_STR)

FRONTEND_DIST_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
)

if os.path.exists(FRONTEND_DIST_DIR):
    assets_dir = os.path.join(FRONTEND_DIST_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{fallback_path:path}")
    async def serve_frontend_spa(fallback_path: str):
        if fallback_path.startswith("api"):
            raise HTTPException(status_code=404, detail="API route not found")

        index_file = os.path.join(FRONTEND_DIST_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return HTMLResponse(
            "Frontend built directory exists but index.html is missing.",
            status_code=404,
        )
else:
    @app.get("/")
    async def default_root_page():
        return HTMLResponse(
            """
            <html>
                <head>
                    <title>TrendCatcher API</title>
                    <style>
                        body { font-family: sans-serif; text-align: center; padding: 50px; background-color: #0f172a; color: #f1f5f9; }
                        a { color: #6366f1; text-decoration: none; font-weight: bold; }
                        a:hover { text-decoration: underline; }
                        .container { max-width: 640px; margin: 0 auto; background: #1e293b; padding: 30px; border-radius: 12px; border: 1px solid #334155; }
                        .footer { margin-top: 20px; font-size: 0.875rem; color: #64748b; }
                        code { color: #cbd5e1; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>TrendCatcher Backend</h1>
                        <p>FastAPI is running successfully. The trend feed is in honest no-live-trends mode until verified social ingestion is connected.</p>
                        <p>Open the API docs at <a href="/api/docs">/api/docs</a>.</p>
                        <p>The frontend bundle was not found at <code>frontend/dist</code> yet.</p>
                    </div>
                </body>
            </html>
            """
        )
