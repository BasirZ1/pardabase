import os
from contextlib import asynccontextmanager
from contextvars import ContextVar

import asyncpg

from dotenv import load_dotenv

load_dotenv(override=True)

current_db = ContextVar("current_db")

# Dictionary to hold async connections for different databases
connection_pools = {}


async def get_connection_pool(db_name):
    """
    Returns a connection pool for the given database name.
    Creates a new pool if it doesn't exist.
    """
    if db_name not in connection_pools:
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")

        connection_pools[db_name] = await asyncpg.create_pool(
            user=db_user,
            password=db_password,
            database=db_name,
            host=db_host,
            port=db_port,
            min_size=1,
            max_size=10  # Adjust based on expected traffic
        )

    return connection_pools[db_name]


def set_current_db(db_name):
    current_db.set(db_name)


async def get_connection():
    """Gets a connection from the pool based on the current database context."""
    db_name = current_db.get()
    pool = await get_connection_pool(db_name)
    conn = await pool.acquire()
    return conn


async def release_connection(conn):
    """Releases the connection back to the pool."""
    db_name = current_db.get()
    pool = await get_connection_pool(db_name)
    await pool.release(conn)


@asynccontextmanager
async def connection_context():
    conn = await get_connection()
    try:
        yield conn
    finally:
        await release_connection(conn)


async def close_all_pools():
    """Closes all connection pools when shutting down the application."""
    for pool in connection_pools.values():
        await pool.close()
