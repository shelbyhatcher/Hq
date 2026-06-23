from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# Since DATABASE_URL is standard for SQLite, connect_args is needed for threading
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def ensure_runtime_schema() -> None:
    """Apply minimal additive schema fixes for deployments without Alembic.

    Base.metadata.create_all creates new tables but does not add columns to an
    existing SQLite database. The live app already has a trends table from older
    builds, so add the verified provenance columns in-place when missing. All
    columns are nullable so legacy seeded/simulated rows stay unverified and are
    withheld by /api/trends.
    """
    inspector = inspect(engine)
    if "trends" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("trends")}
    additive_columns = {
        "source_platform": "VARCHAR(50)",
        "source_external_id": "VARCHAR(100)",
        "source_url": "VARCHAR(500)",
        "source_subreddit": "VARCHAR(100)",
        "source_title": "VARCHAR(500)",
        "source_author": "VARCHAR(100)",
        "source_created_at": "DATETIME",
        "source_collected_at": "DATETIME",
        "source_ingest_method": "VARCHAR(100)",
        "live_source_verified": "BOOLEAN",
        "provenance_json": "TEXT",
    }

    missing_columns = [
        (name, column_type)
        for name, column_type in additive_columns.items()
        if name not in existing_columns
    ]
    if not missing_columns:
        return

    if engine.dialect.name != "sqlite":
        raise RuntimeError(
            "Missing trends provenance columns and no migration path is configured "
            f"for database dialect '{engine.dialect.name}'."
        )

    with engine.begin() as connection:
        for name, column_type in missing_columns:
            connection.exec_driver_sql(f"ALTER TABLE trends ADD COLUMN {name} {column_type}")


# Dependency to get db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
