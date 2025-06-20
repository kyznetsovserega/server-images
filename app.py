from logging.handlers import RotatingFileHandler

from flask import Flask, request, render_template, url_for, redirect, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from typing import Optional
from PIL import Image, UnidentifiedImageError
from datetime import datetime
import psycopg2
import logging
from logging.handlers import RotatingFileHandler
import io
import os
import uuid
from dotenv import load_dotenv

from db_utils import PostgresManager

load_dotenv()

# --- Конфигурация ---
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 МБ
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

# ---Проверка запуска проекта в Docker ---
def is_docker():
    try:
        with open('/proc/1/cgroup', 'rt') as f:
            return 'docker' in f.read() or 'kubepod' in f.read()
    except FileNotFoundError:
        return False

# --- Пути для Docker и локальной среды ---
if is_docker():
    UPLOAD_FOLDER = '/app/images'
    LOG_FOLDER = '/app/logs'
else:
    UPLOAD_FOLDER = 'images'
    LOG_FOLDER = 'logs'

# --- Инициализация Flask ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")

# --- Создание директорий ---
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

# --- Настройка логирования ---
log_file = os.path.join(LOG_FOLDER, 'app.log')
log_handler = RotatingFileHandler(log_file, maxBytes=2_000_000, encoding= 'utf-8')
log_formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log_handler.setFormatter(log_formatter)
logging.getLogger().addHandler(log_handler)
logging.getLogger().setLevel(logging.INFO)

# --- Унифицированное логирование ---
def log_action(message: str, level: str = "info"):
    prefix = {
        "info": "Успех",
        "error": "Ошибка",
        "warning": "Внимание"
    }.get(level.lower(), "Успех")
    if level == "error":
        logging.error(f"{prefix}: {message}")
    elif level == "warning":
        logging.warning(f"{prefix}: {message}")
    else:
        logging.info(f"{prefix}: {message}")

log_action("Сервер запущен.")

# --- Проверка допустимого расширения файла ---
def allowed_file(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower().strip(".")
    return ext in ALLOWED_EXTENSIONS

# --- Генерация уникального имени с именем файла ---
def generate_unique_filename(original: str) -> str:
    name, ext = os.path.splitext(original)
    safe_name = secure_filename(name)
    short_id = uuid.uuid4().hex[:6]
    return f"{safe_name}_{short_id}{ext.lower()}"

# --- Получение размера файла ---
def get_file_size(file) -> int:
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size

# --- Валидация файла перед загрузкой ---
def validate_file(file) -> Optional[str]:
    if not file or not file.filename:
        return "Файл не выбран"
    if not allowed_file(file.filename):
        return "Недопустимый формат файла"
    if get_file_size(file) > MAX_FILE_SIZE:
        return "Файл превышает максимальный размер 5 МБ"

    try:
        img_bytes = file.read()
        Image.open(io.BytesIO(img_bytes)).verify()
        file.seek(0)
    except UnidentifiedImageError:
        return "Файл повреждён или не является изображением"
    except OSError:
        return "Ошибка чтения изображения"
    return None

# --- Главная страница ---
@app.route('/')
def home():
    return render_template('index.html')

# --- Перенаправление на загрузку ---
@app.route('/upload_photos')
def upload_photos_redirect():
    return redirect(url_for('handle_upload'))

# --- Загрузка изображения ---
@app.route('/upload', methods=['GET', 'POST'])
def handle_upload():
    if request.method == 'POST':
        if 'image' not in request.files:
            log_action("Изображение не найдено в запросе", level="error")
            return jsonify({'error': 'Изображение не найдено'}), 400

        file = request.files['image']
        error = validate_file(file)
        if error:
            log_action(error, level="error")
            return jsonify({'error': error}), 400

        filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        try:
            file.save(save_path)
            os.chmod(save_path, 0o664)  # Права доступа
        except Exception as ex:
            log_action(f" Ошибка при сохранении файла {unique_filename}:{ex}", level="error")
            return jsonify({'error': 'Ошибка при сохранении файла'}), 500

        size = os.stat(save_path).st_size # Размер в байтах
        file_type = unique_filename.rsplit('.', 1)[-1].lower()

        # Сохранение метаданные в БД
        try:
            with PostgresManager() as db:
                db.add_image(
                    filename = unique_filename,
                    original_name = filename,
                    size = size,
                    file_type = file_type
                )
        except Exception as ex:
            os.remove(save_path)
            log_action(f"Ошибка при добавлении файла в базу: {ex}", level="error")
            return jsonify({'error': 'Ошибка сохранения в базе'}), 500

        log_action(f"изображение {unique_filename} загружено.")
        return jsonify({'url': f"/images/{unique_filename}"})

    return render_template('upload_photos.html')

# --- Галерея изображений ---
@app.route('/images')
def images_list():
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    per_page = 10
    offset = (page -1 ) * per_page

    try:
        with PostgresManager() as db:
            images = db.get_images(limit = per_page, offset=offset)
            total =db.get_image_count()
    except Exception as ex:
        log_action(f"Ошибка при получении списка изображений: {ex}", level="error")
        images, total = [], 0

    total_pages = (total + per_page - 1) // per_page # Количество страниц

    return render_template(
        'images.html',
        images = images,
        page = page,
        total_pages = total_pages
    )

# --- Удаление изображения по имени ---
@app.route('/delete/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    try:
        with PostgresManager() as db:
            filename = db.delete_image(image_id)
    except Exception as ex:
        log_action(f"Ошибка удаления записи из базы: {ex}", level="error")
        return redirect(url_for('images_list'))

    if filename:
        if isinstance(filename, (tuple, list)):
            filename = filename[0]

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                log_action(f"изображение {filename} удалено.")
            else:
                log_action(f" файл с id {image_id} не найдено для удаления", level="error")
        except Exception as ex:
            log_action(f"Ошибка при удалении файла {filename}: {ex}", level="error")
    else:
        log_action(f"Файл с id {image_id} не найден для удаления", level="error")

    return redirect(url_for('images_list'))

# --- Отдача изображения ---
@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# --- Запуск сервера ---
if __name__ == '__main__':
    log_action(f"Запуск на http://0.0.0.0:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)
