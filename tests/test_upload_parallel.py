import requests
import threading
import time
from log_utils import setup_logging, log_action

setup_logging('logs', 'app.log')

url = 'http://localhost:8000/upload'
file_path = 'tests/test_image.jpg'
num_threads = 10
results = []
statuses = []

def upload():
    with open(file_path, 'rb') as f:
        files = {'image': (file_path, f, 'image/jpeg')}
        start = time.time()
        r = requests.post(url, files=files)
        elapsed = time.time() - start
        results.append(elapsed)
        statuses.append(r.status_code)

threads = []
start_all = time.time()
for _ in range(num_threads):
    t = threading.Thread(target=upload)
    t.start()
    threads.append(t)

for t in threads:
    t.join()
total_time = time.time() - start_all

result = (f'Среднее время загрузки: {sum(results)/len(results):.3f} сек | '
          f'Общее время 10 загрузок: {total_time:.3f} сек')
print(result)
log_action(result, level='info')