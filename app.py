
from flask import Flask, request, render_template, url_for, redirect, flash
from werkzeug.utils import secure_filename
from datetime import datetime
from typing import Optional
import os
import uuid


# Конфигурация
UPLOAD_FOLDER = 'images'
LOG_FOLDER = 'logs'
MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

# Инициализация Фласк-приложения
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "your_secret_key"

# Создание необходимых директорий
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

def allowed_file(filename:str) -> bool:
    """ Проверка допустимого расширения файла """
    ext = os.path.splitext(filename)[1].lower().strip(".")
    return ext in ALLOWED_EXTENSIONS

def log_event(message:str) -> None:
    """ Записывает события в лог-файл"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(os.path.join(LOG_FOLDER, 'app.log'), 'a', encoding='utf-8') as log:
        log.write(f"[{timestamp}] {message}\n")

def generate_unique_filename(original:str) -> str:
    """ Генерирует безопасное уникальное имя файла"""
    ext = original.rsplit('.', 1)[1].lower()
    return f"{uuid.uuid4().hex}.{ext}"

def get_file_size(file) -> int:
    """Определяет размер файла в байтах."""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size

def validate_file(file) -> Optional[str]:
    """Валидация файла (тип и размер)."""
    if not file or not file.filename:
        return "Файл не выбран"
    if not allowed_file(file.filename):
        return "Недопустимый формат"
    if get_file_size(file) > MAX_FILE_SIZE:
        return "Файл больше 5 МБ"
    return None


# --- Маршруты ---
@app.route('/')
def home():
    """Главная страница """
    return render_template('index.html')

@app.route('/upload', methods=['GET','POST'])
def upload():
    """ Страница загрузки"""
    if request.method == 'POST':
        file = request.files.get('image')
        error = validate_file(file)

        if error:
            log_event(f"Ошибка: {error} ({file.filename if file else 'Нет файла'})")
            flash(error,'error')
            return redirect(url_for('upload'))

        filename = secure_filename(file.filename)
        unique_name= generate_unique_filename(filename)
        file.save(os.path.join(UPLOAD_FOLDER, unique_name))

        log_event(f"Успешно загружен: {unique_name}")
        flash(f"Файл успешно загружен! Ссылка: /images/{unique_name}", 'success')
        return redirect(url_for('upload'))

    return render_template('upload_photos.html')

@app.route('/images')
def gallery():
    """ Галерея загруженных изображений """
    files = [f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]
    return render_template('images.html', images=files)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)

