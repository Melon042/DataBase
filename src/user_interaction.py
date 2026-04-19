from pathlib import Path

from src.api import get_employers_to_json, get_vacancies_to_json
from src.files import load_json_to_database
from src.utils import create_db, create_tables
from src.vacancies import DBManager


def user_interaction():
    """Взаимодействие с пользователем через консоль"""

    # Проверяет наличие JSON-файлов.
    # Сделано потому что hh.ru часто выдаёт ошибку 403. (Однажды всё же удалось получить данные)
    employers_file = Path("data") / "employers.json"
    vacancies_file = Path("data") / "vacancies.json"

    if employers_file.exists() and vacancies_file.exists():
        print("Файлы с данными уже существуют. Пропускаю запросы к hh.ru")
    else:
        print("Запрашиваю данные у hh.ru...")
        get_employers_to_json()
        get_vacancies_to_json()

    create_db()
    create_tables()
    load_json_to_database()

    db = DBManager()

    while True:
        print("\n1. Список всех компаний и количество вакансий у каждой компании")
        print("2. Список всех вакансий")
        print("3. Средняя максимальная(до) зарплата по вакансиям с оплатой в рублях")
        print(
            "4. Список всех вакансий, у которых зарплата с оплатой в рублях выше среднего"
        )
        print(
            "5. Поиск вакансий по ключевому слову в названии должности, например python"
        )
        print("6. Выйти")

        choice = input("Выберите действие: ")
        print("")

        if choice == "1":
            data = db.get_companies_and_vacancies_count()

            for i, (c, v) in enumerate(data, 1):
                print(f"{i}. {c}: {v} вакансий")

        elif choice == "2":
            data = db.get_all_vacancies()

            print(f"\nВсего вакансий: {len(data)}\n")

            for i, (company, title, salary_from, salary_to, currency, url) in enumerate(
                data, 1
            ):

                salary_from_str = f"{salary_from}" if salary_from else "(не указано)"
                salary_to_str = f"{salary_to}" if salary_to else "(не указано)"

                if salary_from is None and salary_to is None:
                    salary_str = "Не указана"
                else:
                    currency_str = (
                        f" {('руб.' if currency == 'RUR' else currency)}"
                        if currency
                        else ""
                    )
                    salary_str = (
                        f"от {salary_from_str} до {salary_to_str}{currency_str}"
                    )

                print(f"\n{i}.\nКомпания: {company}")
                print(f"Должность: {title}")
                print(f"Зарплата: {salary_str}")
                print(f"Ссылка: {url}")

        elif choice == "3":
            result = db.get_avg_salary()

            print(f"\nСредняя максимальная(до) зарплата: {int(result)} руб.")

        elif choice == "4":
            data = db.get_vacancies_with_higher_salary()

            print(f"\nВсего вакансий с зарплатой выше среднего: {len(data)}\n")

            for i, (company, title, salary_from, salary_to, url) in enumerate(data, 1):

                salary_from_str = f"{salary_from}" if salary_from else "(не указано)"
                salary_str = f"от {salary_from_str} до {salary_to} руб."

                print(f"\n{i}.\nКомпания: {company}")
                print(f"Должность: {title}")
                print(f"Зарплата: {salary_str}")
                print(f"Ссылка: {url}")

        elif choice == "5":
            query = input("\nВведите слово для поиска: ")

            data = db.get_vacancies_with_keyword(query)

            if data:
                print(f"\nВсего вакансий найдено: {len(data)}\n")

                for i, (
                    company,
                    title,
                    salary_from,
                    salary_to,
                    currency,
                    url,
                ) in enumerate(data, 1):

                    salary_from_str = (
                        f"{salary_from}" if salary_from else "(не указано)"
                    )
                    salary_to_str = f"{salary_to}" if salary_to else "(не указано)"

                    if salary_from is None and salary_to is None:
                        salary_str = "Не указана"
                    else:
                        currency_str = (
                            f" {('руб.' if currency == 'RUR' else currency)}"
                            if currency
                            else ""
                        )
                        salary_str = (
                            f"от {salary_from_str} до {salary_to_str}{currency_str}"
                        )

                    print(f"\n{i}.\nКомпания: {company}")
                    print(f"Должность: {title}")
                    print(f"Зарплата: {salary_str}")
                    print(f"Ссылка: {url}")
            else:
                print("\nВакансий с таким словом в названии должности не найдено.")

        elif choice == "6":
            print("\nРабота программы завершена.")
            break
