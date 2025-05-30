document.addEventListener('DOMContentLoaded', () => {
  const fileInput = document.getElementById('fileInput');
  const uploadBox = document.querySelector('.upload-box');
  const statusTitle = document.getElementById('statusTitle');
  const infoText = document.getElementById('infoText');
  const inputField = document.querySelector('.upload-url input');
  const copyBtn = document.querySelector('.copy-btn');

  // --- Ограничения по типу и размеру файлов ---
  const allowedTypes = ['image/jpg','image/jpeg', 'image/png', 'image/gif'];
  const maxSize = 5 * 1024 * 1024;

  // --- Обработка выбора файла через input ---
  fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    resetState();
    if (!file) return showError('No file selected.');
    if (!allowedTypes.includes(file.type)) return showError('Unsupported format.');
    if (file.size > maxSize) return showError('File too large. Maximum is 5MB.');
    uploadFile(file);
  });

  // --- Drag & Drop функциональность ---
  uploadBox.addEventListener('dragover', e => {
    e.preventDefault();
    uploadBox.classList.add('drag-over');
  });
  uploadBox.addEventListener('dragleave', () => {
    uploadBox.classList.remove('drag-over');
  });
  uploadBox.addEventListener('drop', e => {
    e.preventDefault();
    uploadBox.classList.remove('drag-over');
    fileInput.files = e.dataTransfer.files;
    fileInput.dispatchEvent(new Event('change'));
  });

  // --- Отправка файла на сервер ---
  async function uploadFile(file) {
    infoText.textContent = 'Uploading...';
    try {
      const formData = new FormData();
      formData.append('image', file);
      const response = await fetch('/upload', { method: 'POST', body: formData });
      const data = await response.json();

      if (response.ok && data.url) {
        const url = `${window.location.origin}${data.url}`;
        inputField.value = url;
        statusTitle.textContent = 'File uploaded!';
        statusTitle.style.color = '#0BB07B';
        infoText.textContent = 'Image uploaded successfully.';
      } else {
        showError(data.error || 'Upload failed. No URL returned.');
      }
    } catch (err) {
      showError('Upload failed due to network or server error.');
    }
  }

  // --- Кнопка "COPY" ---
  copyBtn.addEventListener('click', () => {
    const text = inputField.value;
    if (!text) return;
    navigator.clipboard.writeText(text).then(() => {
      copyBtn.textContent = 'COPIED!';
      setTimeout(() => copyBtn.textContent = 'COPY', 1500);
    });
  });

  // --- Функция вывода ошибки ---
  function showError(message) {
    statusTitle.textContent = 'Upload failed';
    statusTitle.style.color = '#FF4C4C';
    infoText.textContent = message;
  }

  // --- Сброс всех полей ---
  function resetState() {
    statusTitle.textContent = 'Select a file or drag and drop here';
    statusTitle.style.color = '#0B0B0B';
    infoText.textContent = 'Only support .jpg, .png and .gif.\nMaximum file size is 5MB';
    inputField.value = '';
  }
});


