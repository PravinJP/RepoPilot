from app.core.database import create_tables
from app.models import Base  # noqa: F401 — imported so models are registered

if __name__ == "__main__":
    create_tables()
    print("Tables created successfully")