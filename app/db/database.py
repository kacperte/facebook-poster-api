from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# configuration for connecting to the database
conf = {
    "host": "db-service",
    "port": "5432",
    "database": "postgres",
    "user": "postgres",
    "password": "postgres",
}

# create the engine for connecting to the database
engine = create_engine(
    "postgresql://{user}:{password}@{host}:{port}/{database}".format(**conf)
)

# create a session local factory for creating sessions to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create a base class for declarative models
Base = declarative_base()


def get_db():
    """Function for getting a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
