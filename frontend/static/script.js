document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const fileInput = document.getElementById('imageUpload');
    const scaleFactor = document.getElementById('scaleFactor').value;
    const optimizedFor = document.getElementById('optimizedFor').value;
    const prompt = document.getElementById('prompt').value;
    const creativity = parseInt(document.getElementById('creativity').value);
    const resemblance = parseInt(document.getElementById('resemblance').value);
    const engine = document.getElementById('engine').value;
    const imagePrice = parseFloat(document.getElementById('imagePriceDesc').value.replace(/[^\d.-]/g, ''));

    if (fileInput.files.length === 0) {
        alert('Пожалуйста, выберите изображение.');
        return;
    }

    const file = fileInput.files[0];

    // Проверка размера файла
    if (file.size > 10 * 1024 * 1024) { // 10 MB
        alert('Размер изображения не должен превышать 10 мегабайт.');
        return;
    }

    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = async function () {
        const base64Image = reader.result.split(',')[1];

        const img = new Image();
        img.onload = async function() {
            const originalWidth = img.width;
            const originalHeight = img.height;

            // Значения по умолчанию
            const defaultValues = {
                scale_factor: "2x",
                optimized_for: "standard",
                prompt: "",
                creativity: 0,
                resemblance: 0,
                engine: "automatic"
            };

            // Текущие значения
            const currentValues = {
                scale_factor: scaleFactor,
                optimized_for: optimizedFor,
                prompt: prompt,
                creativity: creativity,
                resemblance: resemblance,
                engine: engine
            };

            // Формирование тела запроса с измененными значениями
            const requestBody = {
                image: base64Image,
                image_price: imagePrice,
                original_width: originalWidth,
                original_height: originalHeight
            };
            Object.keys(currentValues).forEach(key => {
                if (currentValues[key] !== defaultValues[key]) {
                    requestBody[key] = currentValues[key];
                }
            });

            try {
                console.log('Отправка запроса на сервер...');
                const response = await fetch('/api/image-upscaler', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestBody)
                });

                if (response.ok) {
                    const data = await response.json();
                    console.log('Ответ сервера:', data);
                    const taskId = data.task_id;
                    console.log('Task ID:', taskId);

                    // Отображение анимации "Генерируется..."
                    document.getElementById('result').innerHTML = '<div class="loader"></div>';

                    // Проверка статуса задачи
                    let status = 'IN_PROGRESS';
                    while (status === 'IN_PROGRESS' || status === 'PENDING' || status === 'CREATED') {
                        console.log('Запрос статуса задачи...');
                        const statusResponse = await fetch(`/api/image-upscaler/${taskId}`, {
                            method: 'GET'
                        });
                        const statusData = await statusResponse.json();
                        status = statusData.status;
                        console.log('Статус задачи:', status);
                        if (status === 'COMPLETED') {
                            const imageUrl = statusData.generated[0];

                            // Используем fetch для загрузки файла
                            fetch(imageUrl)
                                .then(response => response.blob())
                                .then(blob => {
                                    // Создаем URL для скачивания Blob-объекта
                                    const downloadUrl = URL.createObjectURL(blob);
                                    const downloadLink = document.createElement('a');
                                    downloadLink.href = downloadUrl;
                                    downloadLink.download = 'upscaled_image.png'; // Указываем имя файла для загрузки
                                    document.body.appendChild(downloadLink);
                                    downloadLink.click();
                                    document.body.removeChild(downloadLink);
                                    URL.revokeObjectURL(downloadUrl); // Очищаем URL после скачивания

                                    // Отображаем результат на странице
                                    document.getElementById('result').innerHTML = `
                                        <img src="${imageUrl}" alt="Увеличенное изображение" style="width: 200px; height: auto;">
                                    `;

                                    // Обновляем баланс после успешного создания изображения
                                    updateBalance();
                                })
                                .catch(error => {
                                    console.error('Ошибка при загрузке файла:', error);
                                    alert('Не удалось скачать файл. Попробуйте ещё раз.');
                                });

                        } else if (status === 'FAILED') {
                            alert('Ошибка при обработке изображения.');
                            document.getElementById('result').innerHTML = '';
                            break;
                        }
                        await new Promise(resolve => setTimeout(resolve, 5000)); // Ожидание 5 секунд перед повторной проверкой
                    }
                } else {
                    const errorData = await response.json();
                    alert('Ошибка: ' + errorData.message);
                }
            } catch (error) {
                alert('Ошибка: ' + error.message);
            }
        };
        img.src = URL.createObjectURL(file);
    };
});

async function updateBalance() {
    try {
        const response = await fetch('/api/get_balance');
        if (response.ok) {
            const data = await response.json();
            document.getElementById('balance').innerText = data.balance;
        } else {
            console.error('Ошибка при получении баланса');
        }
    } catch (error) {
        console.error('Ошибка при получении баланса:', error);
    }
}

// Обновление баланса при загрузке страницы
document.addEventListener('DOMContentLoaded', updateBalance);

// Обновление размера изображения при выборе файла
document.getElementById('imageUpload').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        // Проверка размера файла
        if (file.size > 10 * 1024 * 1024) { // 10 MB
            alert('Размер изображения не должен превышать 10 мегабайт.');
            document.getElementById('imageUpload').value = ''; // Сброс поля выбора файла
            document.getElementById('imageSize').innerText = 'Размер изображения: Не выбрано';
            return;
        }

        const img = new Image();
        img.onload = function() {
            const width = img.width;
            const height = img.height;
            document.getElementById('imageSize').innerText = `Размер изображения: ${width}x${height}`;
        };
        img.src = URL.createObjectURL(file);
    } else {
        document.getElementById('imageSize').innerText = 'Размер изображения: Не выбрано';
    }
});
// Показать/скрыть таблицу с ценами
document.getElementById('showPrices').addEventListener('click', async function() {
    const modal = document.getElementById('pricesTable');
    if (modal.style.display === 'none' || modal.style.display === '') {
        const response = await fetch('/api/get_prices');
        if (response.ok) {
            const prices = await response.json();
            const pricesBody = document.getElementById('pricesBody');
            pricesBody.innerHTML = '';
            prices.forEach(price => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${price.original_width}x${price.original_height}</td>
                    <td>${price.upscale_width}x${price.upscale_height}</td>
                    <td>${price.scale_factor}</td>
                    <td>${price.price}</td>
                `;
                pricesBody.appendChild(row);
            });
            modal.style.display = 'block';
        } else {
            console.error('Ошибка при получении цен');
        }
    } else {
        modal.style.display = 'none';
    }
});

// Закрыть модальное окно
document.querySelector('.close').addEventListener('click', function() {
    document.getElementById('pricesTable').style.display = 'none';
});

// Расчет стоимости обработки изображения
document.getElementById('uploadForm').addEventListener('change', async function() {
    const fileInput = document.getElementById('imageUpload');
    const scaleFactor = document.getElementById('scaleFactor').value;
    const file = fileInput.files[0];
    if (file) {
        const img = new Image();
        img.onload = async function() {
            const originalWidth = img.width;
            const originalHeight = img.height;
            const response = await fetch(`/api/get_price?original_width=${originalWidth}&original_height=${originalHeight}&scale_factor=${scaleFactor}`);
            if (response.ok) {
                const data = await response.json();
                document.getElementById('imagePriceDesc').innerText = `Стоимость обработки: ${data.price} руб.`;
                document.getElementById('imagePriceDesc').value = `${data.price}`;
                document.getElementById('imagePriceDesc').classList.add('price-updated');
            } else {
                console.error('Ошибка при расчете стоимости');
            }
        };
        img.src = URL.createObjectURL(file);
    }
});