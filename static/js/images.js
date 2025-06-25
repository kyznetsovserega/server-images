document.addEventListener('DOMContentLoaded', () => {
  const imagesTable = document.getElementById('imagesTable');
  const emptyMessage = document.getElementById('emptyMessage');
 // const imageList = JSON.parse(imagesTable.dataset.images);

  // --- Если список пуст ---
  if (!Array.isArray(imageList) || imageList.length === 0) {
    emptyMessage.classList.remove('hidden');
    return;
  } else {
    emptyMessage.classList.add('hidden');
  }

  // --- Генерация таблицы изображений ---
  imageList.forEach(img => {
    const row = document.createElement('div');
    row.className = 'image-row';

  // --- Превью изображения ---
  const previewCell = document.createElement('div');
  previewCell.className = 'image-preview-cell';
  const preview = document.createElement('img');
  preview.className = 'image-preview';
  preview.src = `/images/${encodeURIComponent(img[1])}`;
  preview.alt[1];
  //--- Если превью не отражается - заглушка ---
  preview.onerror = () => {
    preview.src = '/static/img_project/icon_image/picture.svg';
  };
  previewCell.appendChild(preview)

  // --- Имя файла (ссылка на просмотр) ---
  const fileCell = document.createElement('div');
  fileCell.className = 'image-filename';
  const link = document.createElement('a');
  link.href = `/images/${encodeURIComponent(img[1])}`;
  link.textContent = img[1];
  link.target = '_blank';
  fileCell.appendChild(link);

  // --- Оригинальное имя ---
  const origCell = document.createElement('div');
  origCell.className = 'image-original';
  origCell.textContent =img[2];

  // --- Размер (кб) ---
  const sizeCell = document.createElement('div');
  sizeCell.className = 'image-size';
  sizeCell.textContent = Math.round(img[3] / 1024);

  // --- Дата загрузки ---э
  const dateCell = document.createElement('div');
  dateCell.className = 'image-date';
  if (img[4]) {
    dateCell.textContent = img[4]; // Просто выводим строку!
  } else {
    dateCell.textContent = '';
  }

  // --- Тип файла ---
  const typeCell = document.createElement('div');
  typeCell.className = 'image-type';
  typeCell.textContent = img[5];

  // --- Кнопка удаления изображения ---
  const delCell = document.createElement('div');
  delCell.className = 'image-delete';
  const delBtn = document.createElement('img');
  delBtn.className = 'delete-icon';
  delBtn.src = '/static/img_project/icon_image/delete_basket.svg';
  delBtn.alt = 'Delete';
  delBtn.addEventListener('click', async () => {
    if (!confirm('Удалить изображение ?')) return;
    try {
      const res = await fetch(`/delete/${img[0]}`, { method: 'POST' });
      if (res.ok) {
        row.remove();
        if (!imagesTable.querySelector('.image-row')) {
          emptyMessage.classList.remove('hidden');
        }
      } else {
        alert('Не удалось удалить изображение.');
      }
    } catch (err) {
      alert('Ошибка удаления: ' +err);
    }
  });
    delCell.appendChild(delBtn);

    // --- Итоговая строка ---
    row.appendChild(previewCell);
    row.appendChild(fileCell);
    row.appendChild(origCell);
    row.appendChild(sizeCell);
    row.appendChild(dateCell);
    row.appendChild(typeCell);
    row.appendChild(delCell);

    imagesTable.appendChild(row);
  });
});










