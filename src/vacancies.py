import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_PARAMS = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


class DBManager:
    """Класс для работы с БД PostgreSQL"""

    def get_companies_and_vacancies_count(self) -> list[tuple[str, int]]:
        """Получает список всех компаний и количество вакансий у каждой компании"""

        conn = psycopg2.connect(**DB_PARAMS)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT name, open_vacancies FROM employers ORDER BY open_vacancies DESC"
            )
            result = cur.fetchall()
        conn.close()
        return result

    def get_all_vacancies(self) -> list[tuple[str, str, float, float, str, str]]:
        """Получает список всех вакансий с указанием компании, названия вакансии, зарплаты и ссылки на вакансию"""

        conn = psycopg2.connect(**DB_PARAMS)
        with conn.cursor() as cur:
            cur.execute(
                """SELECT employers.name, title, salary_from, salary_to, salary_currency, url FROM vacancies
            JOIN employers USING(employer_id)"""
            )
            result = cur.fetchall()
        conn.close()
        return result

    def get_avg_salary(self) -> float:
        """Получает среднюю максимальную(до) зарплату по вакансиям с оплатой в рублях"""

        conn = psycopg2.connect(**DB_PARAMS)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT AVG(salary_to) FROM vacancies WHERE salary_currency = 'RUR' AND salary_to IS NOT NULL"
            )
            result = cur.fetchone()
        conn.close()
        return result[0]

    def get_vacancies_with_higher_salary(
        self,
    ) -> list[tuple[str, str, float, float, str]]:
        """Получает список всех вакансий, у которых зарплата с оплатой в рублях выше средней по всем вакансиям"""

        conn = psycopg2.connect(**DB_PARAMS)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT e.name, v.title, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN employers e USING(employer_id)
                WHERE v.salary_to IS NOT NULL
                AND v.salary_currency = 'RUR'
                AND v.salary_to > (SELECT AVG(salary_to) FROM vacancies
                WHERE salary_currency = 'RUR' AND salary_to IS NOT NULL)
                ORDER BY v.salary_to DESC
            """)
            result = cur.fetchall()
        conn.close()
        return result

    def get_vacancies_with_keyword(
        self, query: str
    ) -> list[tuple[str, str, float, float, str, str]]:
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова, например python"""

        conn = psycopg2.connect(**DB_PARAMS)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT e.name, v.title, v.salary_from, v.salary_to, v.salary_currency, v.url
                FROM vacancies v
                JOIN employers e USING(employer_id)
                WHERE v.title ILIKE %s
                    """,
                (f"%{query}%",),
            )
            result = cur.fetchall()
        conn.close()
        return result
