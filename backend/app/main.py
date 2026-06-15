import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

from app.core.config import settings
from app.api import endpoints

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs"
)

# CORS Setup (Allow frontend development port)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict this to the server host
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(endpoints.router, prefix=settings.API_V1_STR)

# Serve built frontend statically
FRONTEND_DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))

if os.path.exists(FRONTEND_DIST_DIR):
    # Mount assets folder
    assets_dir = os.path.join(FRONTEND_DIST_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
        
    # Catch-all fallback for SPA routes to serve built index.html
    @app.get("/{fallback_path:path}")
    async def serve_frontend_spa(fallback_path: str):
        # Prevent intercepting /api requests
        if fallback_path.startswith("api"):
            raise HTTPException(status_code=404, detail="API route not found")
            
        index_file = os.path.join(FRONTEND_DIST_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
            
        return HTMLResponse("Frontend built directory exists but index.html is missing.", status_code=404)
else:
    # Safe default if frontend has not been compiled yet
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
                        .container { max-width: 600px; margin: 0 auto; background: #1e293b; padding: 30px; border-radius: 12px; border: 1px solid #334155; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>TrendCatcher Backend Skeleton</h1>
                        <p>FastAPI is running successfully in <b>development mode</b>.</p>
                        <p>Access the Swagger API documentation: <a href="/api/docs">/api/docs</a></p>
                        <p>Frontend SPA hasn't been compiled to <code>frontend/dist</code> yet.</p>
                    </div>
                </body>
            </html>
            """
        )
