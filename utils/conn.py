import os

import psycopg2
from dotenv import load_dotenv

load_dotenv(override=True)


def get_connection(db_name="zmt"):
    """
    Returns a PostgreSQL database connection.
    """
    # Access the variables using os.getenv()
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    dsn = f"host={db_host} port={db_port} dbname={db_name} user={db_user} password={db_password}"
    try:
        conn = psycopg2.connect(dsn)
        return conn
    except (Exception, psycopg2.Error) as error:
        print("Error connecting to the database:", error)
        raise error
