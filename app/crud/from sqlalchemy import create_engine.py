from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:Pune2025$@localhost/tdm_portal"

engine = create_engine(
    DATABASE_URL,
    pool_size=30,         # Persistent connections
    max_overflow=30,      # Extra burst connections
    pool_timeout=30,      # Wait time before timeout
    pool_recycle=1800,    # Recycle idle connections
    pool_pre_ping=True    # Auto-check broken connections
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
