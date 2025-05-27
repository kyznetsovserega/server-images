// --- Обработка навигационных вкладок ---
document.addEventListener('DOMContentLoaded', () => {
  const uploadTab = document.getElementById('uploadTab');
  const imagesTab = document.getElementById('imagesTab');

  // --- Переход на /upload при клике, если вкладка не активна ---
  if (uploadTab && !uploadTab.classList.contains('active')) {
    uploadTab.addEventListener('click', () => {
      window.location.href = '/upload';
    });
  }

  // --- Переход на /images при клике, если вкладка не активна ---
  if (imagesTab && !imagesTab.classList.contains('active')) {
    imagesTab.addEventListener('click', () => {
      window.location.href = '/images';
    });
  }
});