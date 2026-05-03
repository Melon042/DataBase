import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.errors import DuplicateDatabase

load_dotenv()

DB_PARAMS = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def create_db() -> None:
    """Создаёт базу данных PostgreSQL"""

    conn = psycopg2.connect(
        host=DB_PARAMS["host"],
        dbname="postgres",
        user=DB_PARAMS["user"],
        password=DB_PARAMS["password"],
    )

    conn.autocommit = True

    try:
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE {DB_PARAMS['dbname']}")
    except DuplicateDatabase:
        pass
    finally:
        conn.close()


def create_tables() -> None:
    """Создаёт таблицы employers и vacancies в БД HHru"""

    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS employers (
            employer_id INTEGER PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            site_url VARCHAR(500),
            hh_url VARCHAR(500),
            open_vacancies INTEGER,
            accredited_it BOOLEAN DEFAULT FALSE
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS vacancies (
            vacancy_id INTEGER PRIMARY KEY,
            employer_id INTEGER NOT NULL REFERENCES employers(employer_id),
            title VARCHAR(150) NOT NULL,
            area VARCHAR(100),
            salary_from NUMERIC,
            salary_to NUMERIC,
            salary_currency VARCHAR(10),
            experience VARCHAR(100),
            employment VARCHAR(100),
            schedule VARCHAR(100),
            snippet_req TEXT,
            snippet_resp TEXT,
            published_at TIMESTAMP,
            url VARCHAR(500)
        );
    """)

    cur.close()
    conn.commit()
    conn.close()
