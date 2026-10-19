"""Secure PostgreSQL connection utilities for Atlas Bank."""

import os
from getpass import getpass

from sqlalchemy import create_engine
from sqlalchemy.engine import URL


def get_db_engine():
    """Create a SQLAlchemy engine without hardcoded credentials."""

    username = os.getenv("ATLAS_DB_USER", "postgres")
    password = os.getenv("ATLAS_DB_PASSWORD")

    if password is None:
        password = getpass("Atlas Bank PostgreSQL password: ")

    host = os.getenv("ATLAS_DB_HOST", "localhost")
    port = int(os.getenv("ATLAS_DB_PORT", "5432"))
    database = os.getenv("ATLAS_DB_NAME", "atlas_bank")

    connection_url = URL.create(
        drivername="postgresql+psycopg2",
        username=username,
        password=password,
        host=host,
        port=port,
        database=database,
    )

    return create_engine(
        connection_url,
        pool_pre_ping=True,
    )
