// --- Обработка навигационных вкладок ---
document.addEventListener('DOMContentLoaded', () => {
  const uploadTab = document.getElementById('uploadTab');
  const imagesTab = document.getElementById('imagesTab');

  if (uploadTab && !uploadTab.classList.contains('active')) {
    uploadTab.addEventListener('click', () => {
      window.location.href = '/upload';
    });
  }
  if (imagesTab && !imagesTab.classList.contains('active')) {
    imagesTab.addEventListener('click', () => {
      window.location.href = '/images';
    });
  }
});