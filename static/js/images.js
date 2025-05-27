document.addEventListener('DOMContentLoaded', () => {
  const imagesTable = document.getElementById('imagesTable');
  const emptyMessage = document.getElementById('emptyMessage');

  // --- Если список пуст — показываем сообщение об отсутствии изображений ---
  if (!Array.isArray(imageList) || imageList.length === 0) {
    emptyMessage.classList.remove('hidden');
    return;
  }

  // --- Обрабатываем каждый файл из imageList ---
  imageList.forEach(imageName => {
    const row = document.createElement('div');
    row.className = 'image-row';

    // --- Превью изображения ---
    const preview = document.createElement('img');
    preview.className = 'image-preview';
    preview.src = `/images/${encodeURIComponent(imageName)}`;
    preview.alt = imageName;
    preview.onerror = () => {
      preview.src = '/static/img_project/icon_image/picture.svg'; // подставляем заглушку
    };

    // --- Блок с именем файла (отображается полностью) ---
    const name = document.createElement('div');
    name.className = 'image-name';
    name.appendChild(preview);
    name.append(document.createTextNode(` ${imageName}`));

    // --- Блок с ссылкой(сокращённый <a>, открывается в новой вкладке) ---
    const url = document.createElement('div');
    url.className = 'image-url';

    const link = document.createElement('a');
    link.href = `${window.location.origin}/images/${encodeURIComponent(imageName)}`;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.className = 'image-link';
    link.textContent = link.href;

    url.appendChild(link);

    // --- Кнопка удаления изображения ---
    const delContainer = document.createElement('div');
    delContainer.className = 'delete-container';

    const delBtn = document.createElement('img');
    delBtn.className = 'delete-icon';
    delBtn.src = '/static/img_project/icon_image/delete_basket.svg';
    delBtn.alt = 'Delete';

    // --- Обработчик клика по кнопке удаления ---
    delBtn.addEventListener('click', async () => {
      const res = await fetch('/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: imageName })
      });

      if (res.ok) {
        row.remove();
        if (!imagesTable.querySelector('.image-row')) {
          emptyMessage.classList.remove('hidden');
        }
      } else {
        alert('⚠️ Не удалось удалить изображение.');
      }
    });

    delContainer.appendChild(delBtn);

    // --- Итоговая строка ---
    row.appendChild(name);
    row.appendChild(url);
    row.appendChild(delContainer);
    imagesTable.appendChild(row);
  });
});










