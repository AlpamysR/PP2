import psycopg2
from config import host, user, password, db_name, port

def get_connection():
    return psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name,
        port=port
    )