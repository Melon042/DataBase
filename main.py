from src.utils import create_db, create_tables
from src.files import load_json_to_database


if __name__ == "__main__":
    create_db()
    create_tables()
    load_json_to_database()
