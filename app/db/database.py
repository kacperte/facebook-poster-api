from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


def read_secret(secret_path):
    with open(secret_path, 'r') as f:
        return f.read().strip()

secrets_dir = '/etc/db-secrets/'

# configuration for connecting to the database
conf = {
    "host": read_secret(f"{secrets_dir}host_db"),
    "port": read_secret(f"{secrets_dir}port_db"),
    "database": read_secret(f"{secrets_dir}database"),
    "user": read_secret(f"{secrets_dir}user_db"),
    "password": read_secret(f"{secrets_dir}password_db")
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
