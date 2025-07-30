document.addEventListener('DOMContentLoaded', () => {
  const imagesTable = document.getElementById('imagesTable');
  const emptyMessage = document.getElementById('emptyMessage');
  const prevBtn = document.getElementById('btn-prev');
  const nextBtn = document.getElementById('btn-next');
  const pageNumEl = document.getElementById('page-number');
  const totalPagesEl = document.getElementById('total-pages');

  let currentPage = Number(pageNumEl.textContent) || 1;

  // --- Безопасный JSON.parse с защитой от пустых ответов ---
  function safeJsonParse(jsonString) {
    // Проверяем, что ответ не пустой и не undefined
    if (!jsonString || jsonString.trim() === "" || jsonString === "undefined") {
      alert("Ошибка: Сервер вернул пустой или некорректный ответ вместо JSON");
      return null;
    }
    try {
      return JSON.parse(jsonString);
    } catch (e) {
      console.error("Ошибка парсинга JSON:", e, jsonString);
      alert("Ошибка парсинга JSON\n" + jsonString);
      return null;
    }
  }

  // --- Загрузка и отображение изображений через API ---
  async function loadImages(page = 1) {
    try {
      const response = await fetch(`/api/images-list?page=${page}`);
      if (!response.ok) throw new Error('Ошибка загрузки изображений');

      // Получаем "сырой" текст
      const text = await response.text();
      console.log('[DEBUG] RAW server response:', text);

      // Защита от пустого ответа прямо здесь
      if (!text || text === "undefined") {
        throw new Error('Сервер вернул пустой ответ или "undefined" вместо JSON');
      }

      const data = safeJsonParse(text);
      if (!data) throw new Error('Ответ от сервера не является валидным JSON');

      const { images, page: serverPage, total_pages } = data;

      // Обновляем номер страницы в DOM и храним актуальную страницу
      pageNumEl.textContent = serverPage;
      totalPagesEl.textContent = total_pages;
      currentPage = serverPage;

      imagesTable.innerHTML = '';

      // Если массив images пустой — показываем "Нет изображений"
      if (!Array.isArray(images) || images.length === 0) {
        if (total_pages > 1 && currentPage !== total_pages) {
          await loadImages(total_pages);
          return;
        }
        emptyMessage.classList.remove('hidden');
        return;
      } else {
        emptyMessage.classList.add('hidden');
      }

      // Отрисовка каждой картинки
      images.forEach(img => {
        const row = document.createElement('div');
        row.className = 'image-row';

        // Превью
        const previewCell = document.createElement('div');
        previewCell.className = 'image-preview-cell';
        const preview = document.createElement('img');
        preview.className = 'image-preview';
        preview.src = `/images/${encodeURIComponent(img[1])}`;
        preview.alt = img[2];
        preview.onerror = () => { preview.src = '/static/img_project/icon_image/picture.svg'; };
        previewCell.appendChild(preview);

        // Имя файла
        const fileCell = document.createElement('div');
        fileCell.className = 'image-filename';
        const link = document.createElement('a');
        link.href = `/images/${encodeURIComponent(img[1])}`;
        let fullFileName = img[1];
        let uniqueName = fullFileName;
        const lastUnderscore = fullFileName.lastIndexOf('_');
        if (lastUnderscore !== -1) {
          uniqueName = fullFileName.substring(lastUnderscore + 1);
        }
        link.textContent = uniqueName;
        link.target = '_blank';
        fileCell.appendChild(link);

        // Оригинальное имя файла
        const origCell = document.createElement('div');
        origCell.className = 'image-original';
        origCell.textContent = img[2];

        // Размер файла
        const sizeCell = document.createElement('div');
        sizeCell.className = 'image-size';
        sizeCell.textContent = Math.round(img[3] / 1024);

        // Дата загрузки
        const dateCell = document.createElement('div');
        dateCell.className = 'image-date';
        dateCell.textContent = img[4] || '';

        // Тип файла
        const typeCell = document.createElement('div');
        typeCell.className = 'image-type';
        typeCell.textContent = img[5];

        // Кнопка удаления
        const delCell = document.createElement('div');
        delCell.className = 'image-delete';
        const delBtn = document.createElement('img');
        delBtn.className = 'delete-icon';
        delBtn.src = '/static/img_project/icon_image/delete_basket.svg';
        delBtn.alt = 'Delete';
        // При нажатии спрашиваем подтверждение и отправляем запрос на удаление
        delBtn.addEventListener('click', async () => {
          if (!confirm('Удалить изображение ?')) return;
          try {
            const res = await fetch(`/delete/${img[0]}?page=${currentPage}`, { method: 'POST' });
            if (res.ok) {
              await loadImages(currentPage);
            } else {
              alert('Не удалось удалить изображение.');
            }
          } catch (err) {
            alert('Ошибка удаления: ' + err);
          }
        });
        delCell.appendChild(delBtn);

        row.appendChild(previewCell);
        row.appendChild(fileCell);
        row.appendChild(origCell);
        row.appendChild(sizeCell);
        row.appendChild(dateCell);
        row.appendChild(typeCell);
        row.appendChild(delCell);

        imagesTable.appendChild(row);
      });

      // --- Включаем/отключаем кнопки пагинации ---
      prevBtn.disabled = (currentPage <= 1);
      nextBtn.disabled = (currentPage >= total_pages);

    } catch (err) {
      imagesTable.innerHTML = '';
      emptyMessage.classList.remove('hidden');
      alert('Ошибка загрузки изображений: ' + err.message);
    }
  }

  // --- Обработчики на кнопки пагинации ---
  prevBtn.addEventListener('click', () => {
    if (currentPage > 1) loadImages(currentPage - 1);
  });
  nextBtn.addEventListener('click', () => {
    if (currentPage < Number(totalPagesEl.textContent)) loadImages(currentPage + 1);
  });

  loadImages(currentPage);
});







