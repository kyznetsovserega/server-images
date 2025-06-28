# Сервер Картинок (Image Server) v2.0

**Web-приложение для загрузки, хранения и просмотра изображений с прямыми ссылками.**

- Хранение метаданных — PostgreSQL  
- Файлы отдает Nginx  
- Контейнеризация — Docker + Docker Compose  
- Поддержка форматов: `.jpg`, `.jpeg`, `.png`, `.gif` до 5 МБ

---

## Технологии

- **Python 3.12, Flask** — backend, REST API
- **Gunicorn** — production WSGI server
- **PostgreSQL** — хранение метаданных изображений
- **Pillow** — валидация и обработка файлов
- **Nginx** — отдача файлов и проксирование API
- **Docker & Docker Compose** — контейнеризация, масштабирование

---

## Быстрый старт

1. **Установите** [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/).
2. **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/kyznetsovserega/server-images.git
    cd server-images
    git checkout v-2.0
    ```
3. **Создайте файл `.env` :** 
    ```bash
    cp .env.example .env
    ```
   (временный файл "for_env")


4. **Запустите проект в Docker:**
    ```bash
    docker compose up --build
    ```
5. **Откройте в браузере:**
    - Интерфейс и загрузка: [http://localhost:8080](http://localhost:8080)
    - Прямая ссылка на файл: [http://localhost:8080/images/<имя_файла>](http://localhost:8080/images/<имя_файла>)
    - (Для отладки: Flask — [http://localhost:8000](http://localhost:8000))


- Все таблицы создаются автоматически при первом запуске через отдельный сервис init_db.

---

## Структура проекта

```
server-images/
│
├── app.py                # Основной backend на Flask
├── backup_db.py          # Скрипт для резервного копирования БД
├── db_utils.py           # Модуль для управления базой данных PostgreSQL
├── log_utils.py          # Централизованный модуль для логирования (rotating logs, форматирование, utf-8)
├── init_db.py            # Автоматическая инициализация структуры таблиц БД через Docker Compose
├── Dockerfile            # Docker-образ приложения
├── docker-compose.yml    # Оркестрация сервисов (Flask, Nginx, PostgreSQL)
├── nginx.conf            # Конфиг для Nginx (reverse proxy + статика)
├── requirements.txt      # Python-зависимости
├── .env                  # Переменные окружения (for_env)
├── .gitignore            # Исключения для git-репозитория
├── .dockerignore         # Исключения для Docker-контекста
│
├── backups/              # [volume] Бэкапы базы данных
│   
├── images/               # [volume] Загруженные пользователями изображения
│   └── .gitkeep
├── logs/                 # [volume] Логи приложения и nginx
│   └── .gitkeep
│
├── static/               # Статические файлы (frontend)
│   ├── favicon.ico
│   ├── img_project/      # Картинки интерфейса (иконки, фоны)
│   │   ├── icon_image/   # SVG-иконки для кнопок/статусов
│   │   └── images_background/   # Фоновые изображения
│   ├── css/              # Стили (отдельно для каждой страницы)
│   └── js/               # JS-скрипты фронтенда
│
├── templates/             # HTML-шаблоны 
│   ├── index.html         # Главная страница
│   ├── upload_photos.html # Интерфейс загрузки файлов
│   └── images-list.html   # Список/галерея изображений
│
├── tests/                         # Тесты производительности
│   ├── test_image.jpg
│   ├── test_upload_one.py        # Проверка загрузки одного изображения   
│   ├── test_upload_parallel.py   # Проверка 10 параллельных загрузок        
│   └── test_nginx_server.py      # Проверка скорости отдачи изображения через Nginx      
│
└── README.md             # Описание и инструкция по проекту
```

---

## API-маршруты
```
| Endpoint                | Метод     | Описание                                  |
|-------------------------|-----------|-------------------------------------------|
| `/`                     | GET       | Главная страница                          |
| `/upload`               | GET/POST  | Форма и процесс загрузки                  |
| `/images-list`          | GET       | Список изображений с пагинацией           |
| `/images/<имя_файла>`   | GET       | Просмотр/скачивание изображения           |
| `/delete/<id>`          | POST      | Удаление изображения по ID                |


```
---

## Структура таблицы `images` (PostgreSQL)

```
```sql
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,        -- Уникальное имя на сервере
    original_name TEXT NOT NULL,   -- Оригинальное имя файла
    size INTEGER NOT NULL,         -- Размер (байт)
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_type TEXT NOT NULL        -- Формат 
);

```
---


## Безопасность

- Только поддерживаемые форматы: .jpg, .jpeg, .png, .gif
- Ограничение размера: до 5 МБ на файл
- Проверка содержимого через Pillow
- Nginx: только методы GET и POST
- HTTP-заголовки защиты (XSS, clickjacking)

---

## Бэкап и восстановление базы данных

Создать резервную копию:
```bash
python backup_db.py
```
- Бэкап-файл появится в папке /backups

Восстановить из бэкапа:
```bash
docker exec -i pg_database psql -U server_images_user server_images_db < backups/<имя_файла>
```

---

## Тесты производительности 

- Загрузка 1 изображения — менее 1 сек

```bash
python tests/test_upload_one.py
```

- 10 параллельных загрузок — менее 1 сек

```bash
python tests/test_upload_parallel.py
```

- Отдача изображения через Nginx — менее 0.1 сек
```bash
 python tests/test_nginx_server.py
```

---


## Автор

Сергей Кузнецов  
[GitHub — @kyznetsovserega](https://github.com/kyznetsovserega)

---
