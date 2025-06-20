from dotenv import load_dotenv
import os
import psycopg2
import logging
import time

load_dotenv()

# Конфиг для подключения к PostgreSQL
db_config = {
    "dbname" : os.getenv("DB_NAME"),
    "user":os.getenv("DB_USER"),
    "password":os.getenv("DB_PASSWORD"),
    "host":os.getenv("DB_HOST", "localhost" ),
    "port":os.getenv("DB_PORT", "5432")
}

# Класс-менеджер для работы с БД
class PostgresManager:
    def __init__(self, config=db_config):
        self.config = config
        self.conn = None
        self.cur = None

    # Открываем соединение с БД
    def __enter__(self):
        for i in range (10):
            try:
                self.conn = psycopg2.connect(**self.config)
                break
            except psycopg2.OperationalError:
                logging.warning("Postgres не готов, пробуем снова...")
                time.sleep(2)
        else:
            raise RuntimeError("Не удалось подключиться к Postgres после 10 попыток")
        self.cur = self.conn.cursor()
        return self

    # Закрываем соединение и курсор при выходе
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    # Создаем таблицу
    def create_table(self):
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
        logging.info("Таблица images проверена/создана.")

    # Добавляем запись в таблицу images
    def add_image(self, filename, original_name, size, file_type):
        try:
            self.cur.execute(
                """
                INSERT INTO images (filename, original_name, size, file_type)
                VALUES (%s,%s,%s,%s)
                """,
                (filename, original_name,size,file_type)
            )
            self.conn.commit()
            logging.info(f"Image {filename} добавлено в базу.")
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Ошибка добавления изображения: {e}")

    # Получаем список всех или части изображений с поддержкой пагинации
    def get_images(self, limit=None, offset=None):
        sql = ("""
            SELECT id, filename, original_name, size, upload_time, file_type
            FROM images ORDER BY upload_time DESC
            """)
        params = []
        if limit is not None:
            sql += "LIMIT %s"
            params.append(limit)
        if offset is not None:
            sql += "OFFSET %s"
            params.append(offset)
        self.cur.execute(sql, tuple(params))
        return self.cur.fetchall()

    # Удаление записи об изображении по id и возвращает имя файла для удаления с диска
    def delete_image(self, image_id):
        self.cur.execute(
            "DELETE FROM images WHERE id = %s RETURNING filename;", (image_id,))
        result = self.cur.fetchone()
        self.conn.commit()
        if result:
            return result[0]
        return None

    # Возвращает общее количество изображений для пагинации
    def get_image_count(self):
        self.cur.execute("SELECT COUNT(*) FROM images;")
        return self.cur.fetchone() [0]


#  Тестовый вызов — для ручной проверки работы менеджера
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    with PostgresManager() as db:
        db.create_table()
        print("Таблица проверена/создана!")
        print("Всего изображений: ", db.get_image_count())
        print("Список изображений: ")
        for img in db.get_images():
            print(img)











































