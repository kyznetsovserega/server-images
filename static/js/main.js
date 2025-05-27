document.addEventListener('DOMContentLoaded', () => {

  // --- Массив изображений для фона ---
  const images = [
    '/static/img_project/images_background/1_back.png',
    '/static/img_project/images_background/2_back.png',
    '/static/img_project/images_background/3_back.png',
    '/static/img_project/images_background/4_back.png',
    '/static/img_project/images_background/5_back.png'
  ];
   // --- Установка случайного изображения в <img id="hero-image"> ---
  const heroImage = document.getElementById('hero-image');
  if (heroImage) {
    const randomImage = images[Math.floor(Math.random() * images.length)];
    heroImage.src = randomImage;
    console.log('Установлен фон:', randomImage);
  }
  // --- Обработка клика по кнопке ---
  const goToPageBtn = document.getElementById('go-to-new-page');
  if (goToPageBtn) {
    goToPageBtn.addEventListener('click', (e) => {
      e.preventDefault();
      window.location.href = '/upload_photos';
    });
  }
});





