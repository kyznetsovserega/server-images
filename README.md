# Сервер Картинок (Image Server) v2.0

Веб-приложение для загрузки, хранения и просмотра изображений.
Пользователь может загрузить `.jpg`, `.jpeg`,`.png` или `.gif` до 5 МБ и получить прямую ссылку на изображение.

---

## Технологии

- **Python 3.12 + Flask** — серверная логика
- **Gunicorn** — продакшен-WGI сервер для многопроцессной обработки
- **Nginx** — отдача изображений и проксирование API
- **Docker & Docker Compose** — развёртывание и масштабирование
- **PostgreSQL** — хранение метаданных
- **Pillow** — валидация подлинности и формата изображений

---

## Быстрый старт

1. **Установи** [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/)
2. **Склонируй репозиторий**:
    ```bash
    git clone https://github.com/kyznetsovserega/server-images.git
    cd server-images
    ```
3. **Запусти проект**:
    ```bash
    docker compose up --build
    ```
4. **Открой**:
    - Главная страница и загрузка: [http://localhost:8080](http://localhost:8080)
    - Прямая ссылка на изображение: [http://localhost:8080/images/<имя_файла>](http://localhost:8080/images/<имя_файла>)
    - (Только для отладки: Flask-бэкенд — [http://localhost:8000](http://localhost:8000))

---

## Структура проекта

```
server-images/
├── app.py                # Flask backend 
├── Dockerfile            # Docker-образ backend
├── docker-compose.yml    # Сервисы Flask + Nginx
├── nginx.conf            # Конфиг Nginx
├── requirements.txt      # Python-зависимости
├── .dockerignore         # Исключения для Docker
├── .gitignore            # Исключения для git
├── README.md             # Документация проекта
├── backup_db.py # Скрипт резервного копирования БД
├── templates/            # HTML-шаблоны
│   ├── index.html            # Главная страница
│   ├── upload_photos.html    # Загрузка изображений
│   └── images.html           # Просмотр файлов
├── static/               # Статика (CSS, JS, картинки)
│   ├── css/                  # Стили
│   ├── js/                   # Скрипты
│   └── img_project/          # Картинки интерфейса
├── images/               # [volume] Все загруженные пользователями изображения 
├── logs/                 # [volume] Логи работы приложения и nginx 

```



##  Маршруты (эндпоинты)

| Endpoint                | Метод     | Описание                                        |
|-------------------------|-----------|-------------------------------------------------|
| `/`                     | GET       | Главная страница                                |
| `/upload`               | GET/POST  | Загрузка изображений                            |
| `/images-list`          | GET       | Список изображений с пагинацией                 |
| `/images/<имя_файла>`   | GET       | Просмотр/скачивание изображения                 |
| `/delete/<id>`          | POST      | Удаление изображения по ID                      |

---

## Структура таблицы images (PostgreSQL)

```sql
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,           -- Сгенерированное уникальное имя файла
    original_name TEXT NOT NULL,      -- Имя, присланное пользователем
    size INTEGER NOT NULL,            -- Размер в байтах
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_type TEXT NOT NULL           -- Формат файла (jpg, png и т.д.)
);


---


## Безопасность

- **Только поддерживаемые форматы:** `.jpg`, `.jpeg`, `.png`, `.gif`
- **Ограничение размера:** до 5 МБ на файл
- **Проверка содержимого:** валидация через Pillow 
- **Nginx:** Разрешены только методы `GET` и `POST` 
- **HTTP-заголовки защиты**


---

## Тесты производительности 

- Загрузка 1 изображения — менее 1 сек
- 10 параллельных загрузок — менее 1 сек
- Отдача изображения через Nginx — менее 0.1 сек

---
## Бэкап и восстановление базы данных

python backup_db.py

Бэкап-файл появится в папке /backups, например: backup_2025-06-25_160130.sql.

## Инструкция по восстановлению бэкапа!!!

docker exec -i pg_database psql -U server_images_user server_images_db < backups/<имя_файла>



## 👤 Автор

Сергей Кузнецов  
[GitHub — @kyznetsovserega](https://github.com/kyznetsovserega)

---
