from sqlalchemy import create_engine, text

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)


def check_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"DB connection error: {type(e).__name__}: {e}")
        return False