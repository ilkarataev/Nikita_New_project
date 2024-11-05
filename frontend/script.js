document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const fileInput = document.getElementById('imageUpload');
    const scaleFactor = document.getElementById('scaleFactor').value;
    const optimizedFor = document.getElementById('optimizedFor').value;
    const prompt = document.getElementById('prompt').value;
    const creativity = parseInt(document.getElementById('creativity').value);
    const hdr = parseInt(document.getElementById('hdr').value);
    const resemblance = parseInt(document.getElementById('resemblance').value);
    const fractality = parseInt(document.getElementById('fractality').value);
    const engine = document.getElementById('engine').value;

    if (fileInput.files.length === 0) {
        alert('Пожалуйста, выберите изображение.');
        return;
    }

    const file = fileInput.files[0];
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = async function () {
        const base64Image = reader.result.split(',')[1];

        // Значения по умолчанию
        const defaultValues = {
            scale_factor: "2x",
            optimized_for: "standard",
            prompt: "",
            creativity: 0,
            hdr: 0,
            resemblance: 0,
            fractality: 0,
            engine: "automatic"
        };

        // Текущие значения
        const currentValues = {
            scale_factor: scaleFactor,
            optimized_for: optimizedFor,
            prompt: prompt,
            creativity: creativity,
            hdr: hdr,
            resemblance: resemblance,
            fractality: fractality,
            engine: engine
        };

        // Формирование тела запроса с измененными значениями
        const requestBody = { image: base64Image };
        Object.keys(currentValues).forEach(key => {
            if (currentValues[key] !== defaultValues[key]) {
                requestBody[key] = currentValues[key];
            }
        });

        try {
            console.log('Отправка запроса на сервер...');
            const response = await fetch('http://127.0.0.1:8000/api/image-upscaler', {
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

                // Отображение сообщения "Генерируется..."
                document.getElementById('result').innerHTML = '<p>Генерируется...</p>';

                // Проверка статуса задачи
                let status = 'IN_PROGRESS';
                while (status === 'IN_PROGRESS' || status === 'PENDING' || status === 'CREATED') {
                    console.log('Запрос статуса задачи...');
                    const statusResponse = await fetch(`http://127.0.0.1:8000/api/image-upscaler/${taskId}`, {
                        method: 'GET'
                    });
                    const statusData = await statusResponse.json();
                    status = statusData.status;
                    console.log('Статус задачи:', status);
                    if (status === 'COMPLETED') {
                        const imageUrl = statusData.generated[0];
                        document.getElementById('result').innerHTML = `
                            <img src="${imageUrl}" alt="Увеличенное изображение" style="width: 200px; height: auto;">
                            <br>
                            <a href="${imageUrl}" download="upscaled_image.png">Скачать изображение</a>
                        `;
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
});