import requests
import time
from log_utils import setup_logging, log_action

setup_logging('logs', 'app.log')

url = 'http://localhost:8000/upload'
file_path = 'tests/test_image.jpg'

with open(file_path, 'rb') as f:
    files = {'image': (file_path, f, 'image/jpeg')}
    start = time.time()
    response = requests.post(url, files=files)
    elapsed = time.time() - start

result = (f'Время загрузки 1 изображения: {elapsed:.3f} сек | '
          f'Статус: {response.status_code} | Ответ: {response.text.strip()}')
print(result)
log_action(result, level='info')