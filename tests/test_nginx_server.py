import os
import requests
import time
from log_utils import setup_logging, log_action

setup_logging('logs', 'app.log')

images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')
files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

if not files:
    result = 'Нет изображений для теста.'
    print(result)
    log_action(result, level='error')
    exit(1)


files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(images_dir, f)), reverse=True)
filename = files[0]
image_url = f'http://localhost:8080/images/{filename}'

start = time.time()
r = requests.get(image_url)
elapsed = time.time() - start

result = f'Время получения изображения: {elapsed:.3f} сек | Статус: {r.status_code} | Файл: {filename}'
print(result)
log_action(result, level='info')