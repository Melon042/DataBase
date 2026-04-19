import json
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def save_to_json(name: str, data: list[dict]) -> None:
    """Функция для сохранения в папку data."""

    os.makedirs(os.path.join(PROJECT_ROOT, "data"), exist_ok=True)
    filepath = os.path.join(PROJECT_ROOT, "data", f"{name}.json")

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


load_dotenv()

DB_PARAMS = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def load_json_to_database() -> None:
    """Загружает данные из json-файлов в базу данных HHru"""

    conn = psycopg2.connect(**DB_PARAMS)

    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM employers LIMIT 1")
        employers_filled = cur.fetchone() is not None
        cur.execute("SELECT 1 FROM vacancies LIMIT 1")
        vacancies_filled = cur.fetchone() is not None

    if employers_filled and vacancies_filled:
        conn.close()
        return

    with open(
        Path(PROJECT_ROOT) / "data" / "employers.json", "r", encoding="utf-8"
    ) as file:
        employers = json.load(file)
    with open(
        Path(PROJECT_ROOT) / "data" / "vacancies.json", "r", encoding="utf-8"
    ) as file:
        vacancies = json.load(file)

    if not employers_filled:
        with conn.cursor() as cur:
            for e in employers:
                cur.execute(
                    """INSERT INTO employers (
                employer_id, name, description, site_url, hh_url, open_vacancies, accredited_it)
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (
                        e["employer_id"],
                        e["name"],
                        e["description"],
                        e["site_url"],
                        e["hh_url"],
                        e["open_vacancies"],
                        e["accredited_it"],
                    ),
                )

    if not vacancies_filled:
        with conn.cursor() as cur:
            for v in vacancies:
                cur.execute(
                    """INSERT INTO vacancies (
                vacancy_id, employer_id, title, area, salary_from, salary_to, salary_currency,
                experience, employment, schedule, snippet_req, snippet_resp, published_at, url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        v["vacancy_id"],
                        v["employer_id"],
                        v["title"],
                        v["area"],
                        v["salary_from"],
                        v["salary_to"],
                        v["salary_currency"],
                        v["experience"],
                        v["employment"],
                        v["schedule"],
                        v["snippet_req"],
                        v["snippet_resp"],
                        v["published_at"],
                        v["url"],
                    ),
                )

    conn.commit()
    conn.close()
