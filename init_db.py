from  db_utils import  PostgresManager
from log_utils import setup_logging, log_action


def main():
    # --- Настройка логирования ---
    setup_logging('logs', 'app.log')

    # --- Создание таблицы images ---
    try:
        with PostgresManager() as db:
            db.create_table()
            log_action("Таблица images проверена/создана (init_db.py)", level="info")
            print("Таблица images проверена/создана!")
    except Exception as ex:
        log_action(f"Ошибка при создании таблицы images (init_db.py): {ex}", level="error")
        print(f"Ошибка при создании таблицы images: {ex}")


if __name__ == '__main__':
    main()