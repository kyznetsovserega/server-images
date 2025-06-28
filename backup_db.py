import os
from datetime import datetime
from dotenv import load_dotenv
from log_utils import setup_logging, log_action

load_dotenv()

setup_logging('logs', 'app.log')

# --- Переменные окружения / параметры ---
CONTAINER = "pg_database"
DB_NAME = os.getenv("DB_NAME", "server_images_db")
DB_USER = os.getenv("DB_USER", "server_images_user")
BACKUP_DIR = "backups"

os.makedirs(BACKUP_DIR, exist_ok=True)
backup_name = f"backup_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.sql"
backup_path = os.path.join(BACKUP_DIR, backup_name)

# --- Команда резервного копирования ---
cmd = f'docker exec -t {CONTAINER} pg_dump -U {DB_USER} {DB_NAME} > {backup_path}'
result = os.system(cmd)
if result == 0:
    log_action(f"Бэкап сохранён : {backup_name}")
    print(f"Бэкап сохранён : {backup_name}")
else:
    log_action(f"ОШИБКА при создании бэкапа : {backup_name}")
    print(f"ОШИБКА при создании бэкапа : {backup_name}")
