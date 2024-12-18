const API_URL = 'http://localhost:5000/appointments';

async function fetchCounts() {
    try {
        const response = await fetch('http://localhost:5000/counts');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        console.log('Counts data:', data);  // Вывод данных в консоль для проверки
        // Обновляем содержимое div с id countDisplay
        document.getElementById('countDisplay').textContent = `Количество записей: ${data.count}`;
    } catch (error) {
        console.error('Ошибка при загрузке количества записей:', error);
        document.getElementById('countDisplay').textContent = 'Ошибка при загрузке количества записей';
    }
}


async function updateCards() {
    try {
        const response = await fetch(API_URL, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error('Ошибка сети');
        }

        const data = await response.json();
        const cardContainer = document.querySelector('.card-container');
        cardContainer.innerHTML = ''; // Очищаем контейнер

        data.appointments.forEach((item, index) => {
            const card = document.createElement('div');
            card.classList.add('card');
            card.innerHTML = `
                <input type="checkbox" id="checkbox-${index}" class="delete-checkbox">
                <h2>${item.fio}</h2>
                <p><strong>Курс:</strong> ${item.course}</p>
                <p><strong>Специальность:</strong> ${item.specialty}</p>
                <p><strong>Телефон:</strong> ${item.phone}</p>
                <p><strong>Запрос:</strong> ${item.query}</p>
                <p><strong>Методы работы:</strong> ${item.preferred_methods}</p>
                <p class="card-time"><strong>Время консультации:</strong> ${item.appointment.day} ${item.appointment.time}</p>
            `;
            cardContainer.appendChild(card);
        });

        // Добавляем кнопку "Удалить выбранные"
        if (data.appointments.length > 0) {
            const deleteButton = document.createElement('button');
            deleteButton.textContent = 'Удалить выбранные';
            deleteButton.classList.add('delete-button');
            deleteButton.addEventListener('click', () => deleteSelectedCards(data));
            cardContainer.appendChild(deleteButton);
        }
    } catch (error) {
        console.error('Ошибка при загрузке данных:', error);
    }
}

async function deleteSelectedCards(data) {
    const checkboxes = document.querySelectorAll('.delete-checkbox');
    const indicesToRemove = [];

    checkboxes.forEach((checkbox, index) => {
        if (checkbox.checked) {
            indicesToRemove.push(index);
        }
    });

    if (indicesToRemove.length > 0) {
        try {
            // Отправляем DELETE-запросы по каждому индексу
            for (const index of indicesToRemove) {
                const response = await fetch(`${API_URL}/${index}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if (!response.ok) {
                    throw new Error('Ошибка при удалении данных');
                }
            }
            // Обновляем карточки после удаления
            updateCards();
        } catch (error) {
            console.error('Ошибка при удалении данных:', error);
        }
    } else {
        alert('Пожалуйста, выберите карточки для удаления.');
    }
}

// Инициализация
updateCards();
fetchCounts();
setInterval(updateCards, 60000);
