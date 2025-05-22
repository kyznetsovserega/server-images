/**
 * upload_photos.js
 * Основная логика загрузки изображений с drag & drop, копированием ссылок и удалением.
 */

document.addEventListener('DOMContentLoaded', () => {
  const fileInput = document.getElementById('fileInput');
  const uploadBox = document.querySelector('.upload-box');
  const infoText = uploadBox.querySelector('.info-text');
  const inputField = document.querySelector('.upload-url input');
  const copyBtn = document.querySelector('.copy-btn');
  const successBlock = document.querySelector('.upload-success');
  const errorBlock = document.querySelector('.upload-failed');
  const imagesTable = document.getElementById('imagesTable');
  const notification = document.querySelector('.notification'); // предполагаем блок уведомлений

  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
  const maxSize = 5 * 1024 * 1024; // 5MB

  fileInput.addEventListener('change', async () => {
    const file = fileInput.files[0];

    // Очистка состояний
    successBlock.classList.add('hidden');
    errorBlock.classList.add('hidden');
    inputField.value = '';
    infoText.textContent = 'Uploading...';

    if (!file) {
      infoText.textContent = 'No file selected.';
      return;
    }

    if (!allowedTypes.includes(file.type)) {
      infoText.textContent = 'Unsupported file format. Only .jpg, .png, .gif allowed.';
      errorBlock.classList.remove('hidden');
      return;
    }

    if (file.size > maxSize) {
      infoText.textContent = 'File too large. Maximum size is 5MB.';
      errorBlock.classList.remove('hidden');
      return;
    }

    const formData = new FormData();
    formData.append('image', file);

    try {
      const response = await fetch('/upload', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        infoText.textContent = 'Upload failed. Server returned an error.';
        errorBlock.classList.remove('hidden');
        return;
      }

      const data = await response.json();

      if (data.url) {
        inputField.value = data.url;
        successBlock.classList.remove('hidden');
        infoText.textContent = 'Upload complete!';
        showNotification('✅ Image uploaded successfully!');
        addImageToList(file.name, data.url);
      } else {
        infoText.textContent = 'Upload failed. No URL returned.';
        errorBlock.classList.remove('hidden');
      }
    } catch (error) {
      console.error(error);
      infoText.textContent = 'Upload failed due to network or server error.';
      errorBlock.classList.remove('hidden');
    }
  });

  // Drag & Drop обработка
  uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.classList.add('drag-over');
  });

  uploadBox.addEventListener('dragleave', () => {
    uploadBox.classList.remove('drag-over');
  });

  uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.classList.remove('drag-over');
    fileInput.files = e.dataTransfer.files;
    fileInput.dispatchEvent(new Event('change'));
  });

  // Копирование ссылки
  copyBtn.addEventListener('click', () => {
    const text = inputField.value;
    if (!text) return;

    navigator.clipboard.writeText(text).then(() => {
      copyBtn.textContent = 'COPIED!';
      showNotification('🔗 Link copied!');
      setTimeout(() => copyBtn.textContent = 'COPY', 1500);
    });
  });

  // Добавление изображения в таблицу
  function addImageToList(name, url) {
    const row = document.createElement('div');
    row.className = 'image-row';

    const img = document.createElement('img');
    img.className = 'image-preview';
    img.src = url;
    img.alt = 'Preview';

    const urlP = document.createElement('p');
    urlP.className = 'image-url';
    urlP.textContent = window.location.origin + '/' + url;

    const del = document.createElement('img');
    del.className = 'delete-icon';
    del.src = 'images_background/icon/feather_trash.svg';
    del.alt = 'Delete';

    // Удаление по клику
    del.addEventListener('click', async () => {
      try {
        const res = await fetch('/delete', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ url })
        });

        if (res.ok) {
          row.remove();
          showNotification('🗑️ Image deleted.');
        } else {
          showNotification('⚠️ Failed to delete on server.');
        }
      } catch (err) {
        console.error(err);
        showNotification('❌ Network error during deletion.');
      }
    });

    row.appendChild(img);
    row.appendChild(urlP);
    row.appendChild(del);
    imagesTable.appendChild(row);
  }

  // Уведомление
  function showNotification(message) {
    if (!notification) return;
    notification.textContent = message;
    notification.classList.add('visible');
    setTimeout(() => {
      notification.classList.remove('visible');
    }, 2000);
  }
});



