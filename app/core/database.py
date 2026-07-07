# alembic init migrations
# alembic revision --autogenerate -m "..."
# alembic upgrade head

import time

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import settings


MAX_RETRIES = 20
RETRY_DELAY = 3


engine = None

for attempt in range(MAX_RETRIES):
    try:
        engine = create_engine(
            settings.SQLALCHEMY_DATABASE_URL,

            # Connection Pool
            pool_pre_ping=True,
            pool_recycle=1800,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
        )

        # تست واقعی اتصال
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        print("✅ Database connected successfully.")
        break

    except OperationalError:
        print(
            f"⏳ Waiting for PostgreSQL... "
            f"({attempt + 1}/{MAX_RETRIES})"
        )

        if attempt == MAX_RETRIES - 1:
            raise

        time.sleep(RETRY_DELAY)


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()