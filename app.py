from flask import Flask, request, render_template, url_for, redirect, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from typing import Optional
from PIL import Image, UnidentifiedImageError
import io
import os
import uuid
from dotenv import load_dotenv
from datetime import datetime

from db_utils import PostgresManager
from log_utils import setup_logging, log_action

load_dotenv()

# --- Конфигурация ---
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 МБ
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

# --- Количество изображений ---
PER_PAGE = 5  # <-- уменьшил до 5, для полного отображения на экране


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
    BACKUP_FOLDER = '/app/backups'
else:
    UPLOAD_FOLDER = 'images'
    LOG_FOLDER = 'logs'
    BACKUP_FOLDER = 'backups'


# --- Инициализация Flask ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")

# --- Создание директорий ---
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)

# --- Настройка логирования ---
setup_logging(LOG_FOLDER, 'app.log')

log_action("Сервер запущен.")


# --- Форматирование даты ---
def format_upload_time(dt):
    if isinstance(dt, datetime):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(dt, str):
        return dt[:19]
    return ''


# --- Проверка допустимого расширения файла ---
def allowed_file(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower().strip(".")
    if not ext:
        return False
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


# --- Обработка ошибок для API (404/500) ---
@app.errorhandler(404)
def not_found_error(_error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Не найдено'}), 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(_error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500
    return render_template('500.html'), 500


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
            # Если формат не тот — ошибка 415, иначе 400
            return jsonify({'error': error, 'status': 'fail'}), 415 if "формат" in error.lower() else 400

        filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        try:
            file.save(save_path)
            os.chmod(save_path, 0o664)  # Права доступа
        except Exception as ex:
            log_action(f" Ошибка при сохранении файла {unique_filename}:{ex}", level="error")
            return jsonify({'error': 'Ошибка при сохранении файла'}), 500

        size = os.stat(save_path).st_size  # Размер в байтах
        file_type = unique_filename.rsplit('.', 1)[-1].lower()

        # Сохранение метаданные в БД
        try:
            with PostgresManager() as db:
                db.add_image(
                    filename=unique_filename,
                    original_name=filename,
                    size=size,
                    file_type=file_type
                )
        except Exception as ex:
            os.remove(save_path)
            log_action(f"Ошибка при добавлении файла в базу: {ex}", level="error")
            return jsonify({'error': 'Ошибка сохранения в базе'}), 500

        log_action(f"изображение {unique_filename} загружено.")
        return jsonify({
            'url': f"/images/{unique_filename}",
            'filename': unique_filename,
            'status': 'success'
        }), 200

    return render_template('upload_photos.html', images=[])


# --- API endpoint для динамического получения списка изображений ---
@app.route('/api/images-list')
def api_images_list():
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    per_page = PER_PAGE
    offset = (page - 1) * per_page

    try:
        with PostgresManager() as db:
            total = db.get_image_count()
            total_pages = max(1, (total + per_page - 1) // per_page)
            if page > total_pages and total > 0:
                page = total_pages
                offset = (page - 1) * per_page
            images = db.get_images(limit=per_page, offset=offset)
    except Exception as ex:
        log_action(f"[API] Ошибка при получении списка изображений: {ex}", level="error")
        images, total, total_pages = [], 0, 1

    formatted_images = []
    for img in images:
        upload_time_str = format_upload_time(img[4])
        formatted_images.append(
            (img[0], img[1], img[2], img[3], upload_time_str, img[5])
        )

    # Логируем возвращаемый ответ API
    response_obj = {
        'images': formatted_images,
        'page': page,
        'total_pages': max(1, (total + per_page - 1) // per_page)
    }
    log_action(f"[API] /api/images-list: Response: {response_obj}")

    return jsonify(response_obj)


# --- Страница галереи изображений с пагинацией ---
@app.route('/images-list')
def images_list():
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    per_page = PER_PAGE
    offset = (page - 1) * per_page

    try:
        with PostgresManager() as db:
            total = db.get_image_count()
            total_pages = max(1, (total + per_page - 1) // per_page)
            if page > total_pages and total > 0:
                # Логируем ситуацию
                log_action(f"[IMAGES-LIST] Пустая страница {page}, редирект на последнюю существующую {total_pages}",
                           level="info")
                return redirect(url_for('images_list', page=total_pages))

            # Получаем только нужную страницу
            images = db.get_images(limit=per_page, offset=offset)
            # --- Если на странице нет файлов, а страница не первая — редиректим на предыдущую ---
            if not images and page > 1:
                log_action(f"[IMAGES-LIST] На странице {page} не найдено файлов, редирект на {page - 1}", level="info")
                return redirect(url_for('images_list', page=page - 1))

    except Exception as ex:
        log_action(f"Ошибка при получении списка изображений: {ex}", level="error")
        images, total, total_pages = [], 0, 1

    # Пересчёт total_pages после получения изображений
    total_pages = (total + per_page - 1) // per_page  # Количество страниц

    # --- Формируем дату ---
    formatted_images = []
    for img in images:
        upload_time_str = format_upload_time(img[4])
        formatted_images.append(
            (img[0], img[1], img[2], img[3], upload_time_str, img[5])
        )

    return render_template(
        'images-list.html',
        images=formatted_images,
        page=page,
        total_pages=total_pages
    )


# --- Удаление изображения по id ---
@app.route('/delete/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    page = int(request.args.get('page', 1))
    per_page = PER_PAGE

    log_action(f"[DELETE] Запрос на удаление image_id={image_id} со страницы page={page}", level="info")
    try:
        with PostgresManager() as db:
            log_action(f"[DELETE] Получение списка всех id изображений (для вычисления позиции)", level="info")
            all_images = db.get_images()
            image_ids = [img[0] for img in all_images]
            total_files = len(image_ids)
            log_action(f"[DELETE] Всего файлов до удаления: {total_files}. Все id: {image_ids}", level="info")

            # Находим индекс удаляемого файла
            try:
                idx = image_ids.index(image_id)
                log_action(f"[DELETE] Индекс удаляемого файла: {idx}", level="info")
            except ValueError:
                idx = None
                log_action(f"[DELETE] Файл с id={image_id} не найден в списке image_ids!", level="error")

            # Удаляем файл из базы и с диска
            filename = db.delete_image(image_id)
            log_action(f"[DELETE] После db.delete_image: filename={filename}", level="info")
            if filename:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                        log_action(f"[DELETE] Файл {filename} удалён с диска.", level="info")
                    except Exception as ex:
                        log_action(f"[DELETE] Ошибка при удалении файла {filename}: {ex}", level="error")
                else:
                    log_action(f"[DELETE] Файл {filename} не найден на диске для удаления.", level="warning")
            else:
                log_action(f"[DELETE] Файл с id {image_id} не найден в базе для удаления", level="error")

            # После удаления — сдвигаем все следующие файлы вперед
            if idx is not None and idx < total_files - 1:
                log_action(f"[DELETE] (Логика сдвига) Уплотнение произойдет при рендере (LIMIT/OFFSET).", level="info")

            # После удаления - вычисляем новое количество файлов
            new_total = db.get_image_count()
            last_page = max(1, (new_total + per_page - 1) // per_page)
            log_action(f"[DELETE] Файлов после удаления: {new_total}, last_page={last_page}, текущая страница={page}",
                       level="info")
            # Проверяем, остались ли файлы на текущей странице
            offset = (page - 1) * per_page
            images_after = db.get_images(limit=per_page, offset=offset)
            if not images_after and page > 1:
                log_action(f"[DELETE] На странице {page} не осталось файлов после удаления, редирект на {page - 1}",
                           level="info")
                page = page - 1

            if page > last_page:
                log_action(f"[DELETE] Перенаправляем пользователя на последнюю существующую страницу {last_page}",
                           level="info")
                page = last_page

    except Exception as ex:
        log_action(f"[DELETE] ОШИБКА при удалении: {ex}", level="error")
        return redirect(url_for('images_list', page=page))

    log_action(f"[DELETE] Удаление завершено, редирект на страницу {page}", level="info")
    return redirect(url_for('images_list', page=page))


# --- Отдача изображения ---
@app.route('/images/<filename>')
def server_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# --- Запуск сервера ---
if __name__ == '__main__':
    log_action(f"Запуск на http://0.0.0.0:8000")
    app.run(host='0.0.0.0', port=8000, debug=os.environ.get("FLASK_ENV") == "development")
