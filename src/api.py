import requests
import time
from src.files import save_to_json


BASE_URL = "https://api.hh.ru"
HEADERS = {"User-Agent": "StudyProject/1.0 (dimonka1000@gmail.com)"}
EMPLOYERS_IDS = ["2180", "87021", "1740", "78638", "80", "2748", "3776", "4219", "4934", "1122462"]


def get_employers_to_json() -> None:
    """Получает данные о работодателях через API и сохраняет в JSON-файл."""

    employers_data = []

    for employer_id in EMPLOYERS_IDS:
        response = requests.get(f"{BASE_URL}/employers/{employer_id}", headers=HEADERS)
        if response.status_code != 200:
            print(f"Ошибка {response.status_code} при запросе данных о компании {employer_id}.")
            continue

        data = response.json()
        employers_data.append({
            "employer_id": int(data["id"]),
            "name": data["name"],
            "description": data.get("description", ""),
            "site_url": data.get("site_url", ""),
            "hh_url": data.get("alternate_url", ""),
            "open_vacancies": int(data["open_vacancies"]),
            "accredited_it": bool(data.get("accredited_it_employer", False))
        })

        time.sleep(0.2)

    save_to_json("employers", employers_data)


def get_vacancies_to_json() -> None:
    """Получает вакансии работодателей через API и сохраняет в JSON-файл.
    (Лимитировано до max 200 вакансий на компанию для экономии времени и места)"""

    vacancies = []

    for employer_id in EMPLOYERS_IDS:
        page = 0
        while True:
            params = {"employer_id": employer_id, "per_page": 100, "page": page}
            response = requests.get(f"{BASE_URL}/vacancies", headers=HEADERS, params=params)
            if response.status_code != 200:
                print(f"Ошибка {response.status_code} при запросе вакансий компании {employer_id}.")
                break

            data = response.json()
            items = data.get("items", [])
            if not items:
                break

            for v in items:
                salary = v.get("salary") or {}
                vacancies.append({
                    "vacancy_id": int(v["id"]),
                    "employer_id": int(employer_id),
                    "title": v["name"],
                    "area": v["area"]["name"],
                    "salary_from": salary.get("from"),
                    "salary_to": salary.get("to"),
                    "salary_currency": salary.get("currency"),
                    "experience": v.get("experience", {}).get("name", ""),
                    "employment": v.get("employment", {}).get("name", ""),
                    "schedule": v.get("schedule", {}).get("name", ""),
                    "snippet_req": v.get("snippet", {}).get("requirement", ""),
                    "snippet_resp": v.get("snippet", {}).get("responsibility", ""),
                    "published_at": v.get("published_at", ""),
                    "url": v.get("alternate_url", "")
                })

            if len(items) < 100:
                break
            page += 1
            if page == 2:
                break
            time.sleep(1)

    save_to_json("vacancies", vacancies)
