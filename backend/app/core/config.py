import os

class Settings:
    PROJECT_NAME: str = "TrendCatcher API"
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./trendcatcher.db")
    
    # AI Keys (Placeholder)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY", "")

settings = Settings()
