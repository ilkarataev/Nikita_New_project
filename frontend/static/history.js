async function loadHistory() {
    const response = await fetch(`/api/images_urls/${email}`);
    if (response.ok) {
        const images = await response.json();
        const container = document.getElementById('historyContainer');
        for (const url of images) {
            const img = document.createElement('img');
            img.src = url;
            img.style.width = '200px';
            img.style.height = '200px';
            img.style.margin = '10px';
            container.appendChild(img);

            const downloadLink = document.createElement('a');
            downloadLink.href = `/api/download_image?url=${encodeURIComponent(url)}`;
            downloadLink.innerText = 'Скачать';
            downloadLink.addEventListener('click', async function(event) {
                event.preventDefault();
                const response = await fetch(downloadLink.href);
                if (response.ok) {
                    const blob = await response.blob();
                    const downloadUrl = URL.createObjectURL(blob);
                    const tempLink = document.createElement('a');
                    tempLink.href = downloadUrl;
                    tempLink.download = 'image.png';
                    document.body.appendChild(tempLink);
                    tempLink.click();
                    document.body.removeChild(tempLink);
                    URL.revokeObjectURL(downloadUrl);
                } else {
                    console.error('Ошибка при скачивании файла');
                }
            });
            container.appendChild(downloadLink);
        }
    } else {
        console.error('Ошибка при загрузке истории');
    }
}

// Загрузка всех изображений при загрузке страницы
document.addEventListener('DOMContentLoaded', loadHistory);