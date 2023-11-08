from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import DATABASE_URL, ENV

# ca_path = "/etc/ssl/certs/ca-certificates.crt"
# ssl_args = {"ssl_ca": ca_path}

if ENV == "LOCAL":
    ssl_args = {}
else:
    ssl_args = {"ssl": {"ca": "/etc/ssl/certs/ca-certificates.crt"}}
engine = create_engine(
    DATABASE_URL,
    echo=False,
    query_cache_size=0,
    connect_args=ssl_args,
    pool_timeout=1,
    pool_size=30,
    max_overflow=50,
)


# Dependency
def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# db = SessionLocal()

Base = declarative_base()
