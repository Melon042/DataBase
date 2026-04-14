import os
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

def save_to_json(name: str, data: list[dict]):
    """Функция для сохранения в папку data."""

    os.makedirs(os.path.join(PROJECT_ROOT, "data"), exist_ok=True)
    filepath = os.path.join(PROJECT_ROOT, "data", f"{name}.json")

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
