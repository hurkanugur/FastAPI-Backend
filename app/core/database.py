from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import DBSettings

# Load DB settings
db_settings = DBSettings()

# PostgreSQL URL
DATABASE_URL = (
    f"postgresql://{db_settings.postgres_user}:{db_settings.postgres_password}"
    f"@{db_settings.postgres_host}:{db_settings.postgres_port}/{db_settings.postgres_db}"
)

# Create engine
engine = create_engine(DATABASE_URL, echo=True, future=True)

# SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
