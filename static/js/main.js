// Ждём загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
  // Список изображений для случайного фона (пути с /static)
const images = [
  '/static/images/images_background/1_back.png',
  '/static/images/images_background/2_back.png',
  '/static/images/images_background/3_back.png',
  '/static/images/images_background/4_back.png',
  '/static/images/images_background/5_back.png',
];



  // Установка случайного изображения в <img id="hero-image">
  const heroImage = document.getElementById('hero-image');
  if (heroImage) {
    const randomImage = images[Math.floor(Math.random() * images.length)];
    heroImage.src = randomImage;
    console.log('Установлен фон:', randomImage);
  } else {
    console.warn('Элемент hero-image не найден');
  }

  // Обработка клика по кнопке перехода
  const goToPageBtn = document.getElementById('go-to-new-page');
  if (goToPageBtn) {
    goToPageBtn.addEventListener('click', function (event) {
      event.preventDefault();
      window.location.href = '/upload_photos';
    });
  }
});




