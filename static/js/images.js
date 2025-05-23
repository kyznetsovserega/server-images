document.addEventListener('DOMContentLoaded', () => {
  const imagesTable = document.getElementById('imagesTable');
  const emptyMessage = document.getElementById('emptyMessage');

  if (!Array.isArray(imageList) || imageList.length === 0) {
    emptyMessage.classList.remove('hidden');
    return;
  }

  imageList.forEach(imageName => {
    const row = document.createElement('div');
    row.className = 'image-row';

    const img = document.createElement('img');
    img.className = 'image-preview';
    img.src = `/images/${encodeURIComponent(imageName)}`;
    img.alt = imageName;
    img.onerror = () => {
      img.src = '/static/img_project/icon_image/picture.svg';
    };

    const name = document.createElement('p');
    name.className = 'image-name';
    name.textContent = imageName;

    const url = document.createElement('p');
    url.className = 'image-url';
    url.textContent = `${window.location.origin}/images/${encodeURIComponent(imageName)}`;

    const del = document.createElement('img');
    del.className = 'delete-icon';
    del.src = '/static/img_project/icon_image/delete_basket.svg';
    del.alt = 'Delete';

    del.addEventListener('click', async () => {
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
        alert('⚠️ Failed to delete image.');
      }
    });

    row.appendChild(img);
    row.appendChild(url);
    row.appendChild(del);
    imagesTable.appendChild(row);
  });
});








