import os
from datetime import datetime

CONTAINER = "pg_database"
DB_NAME = os.getenv("DB_NAME", "server_images_db" )
DB_USER = os.getenv("DB_USER", "server_images_user")
BACKUP_DIR = "backups"

os.makedirs(BACKUP_DIR, exist_ok=True)
backup_name = f"backup_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.sql"
backup_path = os.path.join(BACKUP_DIR, backup_name)

cmd = f'docker exec -t {CONTAINER} pg_dump -U {DB_USER} {DB_NAME} > {backup_path}'
result =os.system(cmd)
if result == 0:
    print(f"Бэкап сохранён : {backup_name}")
else:
    print(f"ОШИБКА при создании бэкапа!")