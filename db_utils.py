from dotenv import load_dotenv
import os
import psycopg2
import time
from log_utils import log_action, setup_logging

load_dotenv()

# --- Конфиг для подключения к PostgreSQL ---
db_config = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}


# --- Класс-менеджер для работы с БД ---
class PostgresManager:
    def __init__(self, config=None):
        if config is None:
            config = db_config
        self.config = config
        self.conn = None
        self.cur = None

    # --- Открываем соединение с БД ---
    def __enter__(self):
        for i in range(10):
            try:
                self.conn = psycopg2.connect(**self.config)
                self.cur = self.conn.cursor()
                break
            except psycopg2.OperationalError as ex:
                log_action(f"[DB] Postgres не готов, попытка {i + 1}/10: {ex}")
                time.sleep(2)
        else:
            raise RuntimeError("Не удалось подключиться к Postgres после 10 попыток")
        return self

    # --- Закрываем соединение и курсор при выходе ---
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    # --- Создаем таблицу ---
    def create_table(self):
        try:
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id SERIAL PRIMARY KEY,
                    filename TEXT NOT NULL,
                    original_name TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_type  TEXT NOT NULL
                    );
            """)
            self.conn.commit()
            log_action("Таблица images проверена/создана.")
        except Exception as ex:
            self.conn.rollback()
            log_action(f"Ошибка создания таблицы images: {ex}")

    # --- Добавляем запись в таблицу images ---
    def add_image(self, filename, original_name, size, file_type):
        try:
            self.cur.execute(
                """
                INSERT INTO images (filename, original_name, size, file_type)
                VALUES (%s,%s,%s,%s)
                """,
                (filename, original_name, size, file_type)
            )
            self.conn.commit()
            print(f"Image {filename} добавлено в базу.")
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка добавления изображения: {e}")

    # --- Получаем список всех или части изображений с поддержкой пагинации ---
    def get_images(self, limit=None, offset=None):
        sql = """
            SELECT id, filename, original_name, size, upload_time, file_type
            FROM images ORDER BY upload_time DESC
        """
        params = []
        if limit is not None:
            sql += " LIMIT %s"
            params.append(limit)
        if offset is not None:
            sql += " OFFSET %s"
            params.append(offset)
        try:
            self.cur.execute(sql, tuple(params))
            return self.cur.fetchall()
        except Exception as ex:
            log_action(f"Ошибка выборки изображений: {ex}")
            return []

    # Удаление записи об изображении по id и возвращает имя файла для удаления с диска
    def delete_image(self, image_id):
        try:
            self.cur.execute(
                "DELETE FROM images WHERE id = %s RETURNING filename;", (image_id,))
            result = self.cur.fetchone()
            self.conn.commit()
            if result:
                return result[0]
            return None
        except Exception as ex:
            self.conn.rollback()
            log_action(f"Ошибка удаления изображения: {ex}")
            return None

    # Возвращает общее количество изображений для пагинации
    def get_image_count(self):
        try:
            self.cur.execute("SELECT COUNT(*) FROM images;")
            return self.cur.fetchone()[0]
        except Exception as ex:
            log_action(f"Ошибка подсчёта изображений: {ex}")
            return 0


#  Тестовый вызов — для ручной проверки работы менеджера
if __name__ == '__main__':
    setup_logging('logs', 'app.log')
    with PostgresManager() as db:
        db.create_table()
        print("Таблица проверена/создана!")
        print("Всего изображений: ", db.get_image_count())
        print("Список изображений: ")
        for img in db.get_images():
            print(img)
