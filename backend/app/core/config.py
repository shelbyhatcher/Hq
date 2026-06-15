import os


class Settings:
    PROJECT_NAME: str = "TrendCatcher API"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./trendcatcher.db")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY", "")
    AUTH_SECRET_KEY: str = os.getenv("AUTH_SECRET_KEY", "trendcatcher-dev-auth-key")


settings = Settings()
