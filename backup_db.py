import os
from datetime import datetime
import logging
from dotenv import load_dotenv

# Грузим .env
load_dotenv()

logging.basicConfig(filename='logs/app.log', level=logging.INFO)  # исправлено level

CONTAINER = "pg_database"
DB_NAME = os.getenv("DB_NAME", "server_images_db")         # значение по умолчанию
DB_USER = os.getenv("DB_USER", "server_images_user")       # значение по умолчанию
BACKUP_DIR = "backups"

os.makedirs(BACKUP_DIR, exist_ok=True)
backup_name = f"backup_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.sql"
backup_path = os.path.join(BACKUP_DIR, backup_name)

cmd = f'docker exec -t {CONTAINER} pg_dump -U {DB_USER} {DB_NAME} > {backup_path}'
result = os.system(cmd)
if result == 0:
    logging.info(f"Бэкап сохранён : {backup_name}")
else:
    logging.error(f"ОШИБКА при создании бэкапа : {backup_name}")

# Запуск
# python backup_db.py
# cmd = f'docker exec -t {CONTAINER} pg_dump -U {DB_USER} {DB_NAME} > {backup_path}'
