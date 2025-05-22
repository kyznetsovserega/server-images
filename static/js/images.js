document.addEventListener('DOMContentLoaded', () => {
  const images = [
    { name: 'photo1.jpg', url: 'uploads/photo1.jpg' },
    { name: 'meme2.png', url: 'uploads/meme2.png' },
    { name: 'funny3.gif', url: 'uploads/funny3.gif' }
  ];

  const imagesTable = document.getElementById('imagesTable');

  images.forEach(image => {
    const row = document.createElement('div');
    row.className = 'image-row';

    const img = document.createElement('img');
    img.className = 'image-preview';
    img.src = '/' + image.url;
    img.alt = 'Preview';

    const url = document.createElement('p');
    url.className = 'image-url';
    url.textContent = window.location.origin + '/' + image.url;

    const del = document.createElement('img');
    del.className = 'delete-icon';
    del.src = '/static/images/icon_image/delete_basket.svg';
    del.alt = 'Delete';

    del.addEventListener('click', () => {
      row.remove();
      // TODO: отправить запрос на сервер для удаления файла
    });

    row.appendChild(img);
    row.appendChild(url);
    row.appendChild(del);
    imagesTable.appendChild(row);
  });
});





