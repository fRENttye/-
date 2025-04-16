document.addEventListener('DOMContentLoaded', function() {
    const chatIcon = document.getElementById('chat-icon');
    const chatContainer = document.getElementById('chat-container');
    const closeButton = document.getElementById('close-button');
    const chatBox = document.getElementById('chat-box');

    // Показать чат при нажатии на иконку
    chatIcon.addEventListener('click', function() {
        chatContainer.style.display = 'block'; // Показываем контейнер чата
        chatIcon.style.display = 'none'; // Скрываем иконку (если хотите)
    });

    // Закрыть чат при нажатии на кнопку закрытия
    closeButton.addEventListener('click', function() {
        chatContainer.style.display = 'none'; // Скрываем контейнер чата
        chatIcon.style.display = 'flex'; // Показываем иконку снова
    });

    // Обработка нажатий на инлайн-кнопки
    const inlineButtons = document.querySelectorAll('.inline-button');

    inlineButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textMessage = this.getAttribute('data-message'); // Получаем сообщение из атрибута

            appendMessage("", textMessage, "user"); // Добавляем сообщение пользователя в чат

            // Показать "Печатает..." перед ответом бота
            const typingIndicator = showTypingIndicator();

            setTimeout(() => {
                hideTypingIndicator(typingIndicator); // Скрыть индикатор печати через 2 секунды

                setTimeout(() => {
                    const botResponse = getBotResponse(textMessage);
                    appendMessage("", botResponse, "bot"); // Добавляем ответ бота в чат
                }, 500); // Задержка 0.5 секунды перед выводом ответа бота
            }, 2000); // Задержка 2 секунды для индикатора печати
        });
    });

    function appendMessage(sender, text, type) {
        const messageElement = document.createElement('div'); // Создаем новый элемент для сообщения
        messageElement.textContent = `${sender} ${text}`; // Устанавливаем текст сообщения

        if (type === "user") {
            messageElement.classList.add("user-message"); // Добавляем класс для сообщения пользователя
        } else if (type === "bot") {
            messageElement.classList.add("bot-message"); // Добавляем класс для сообщения бота
        }

        chatBox.appendChild(messageElement); // Добавляем сообщение в чат
        chatBox.scrollTop = chatBox.scrollHeight; // Прокручиваем вниз к последнему сообщению

        // Плавная анимация появления сообщения
        messageElement.style.opacity = 0;
        let opacity = 0;
        const fadeInInterval = setInterval(() => {
            if (opacity < 1) {
                opacity += 0.1;
                messageElement.style.opacity = opacity;
            } else {
                clearInterval(fadeInInterval);
            }
        }, 50); // Интервал для плавного появления сообщения
    }

    function showTypingIndicator() {
        const typingIndicator = document.createElement('div');
        typingIndicator.textContent = "Бот печатает...";
        typingIndicator.classList.add("typing-indicator");
        
        chatBox.appendChild(typingIndicator);
        
        typingIndicator.style.opacity = 0;
        
        let opacity = 0;
        const fadeInInterval = setInterval(() => {
            if (opacity < 1) {
                opacity += 0.1;
                typingIndicator.style.opacity = opacity;
            } else {
                clearInterval(fadeInInterval);
            }
        }, 50); // Интервал для плавного появления индикатора печати
        
        return typingIndicator; 
    }

    function hideTypingIndicator(typingIndicator) {
        if (typingIndicator) {
            let opacity = 1;
            const fadeOutInterval = setInterval(() => {
                if (opacity > 0) {
                    opacity -= 0.1;
                    typingIndicator.style.opacity = opacity;
                } else {
                    clearInterval(fadeOutInterval);
                    typingIndicator.remove(); // Удаляем индикатор после исчезновения
                }
            }, 50); // Интервал для плавного исчезновения индикатора печати
        }
    }

function getBotResponse(userMessage) {
    userMessage = userMessage.toLowerCase(); // Приводим сообщение к нижнему регистру для упрощения сравнения

    if (userMessage.includes("какие функции поддерживает телеграмм бот?")) {
        return "Телеграмм бот поддерживает поиск музыки, просмотр погоды, и переводить текст.";
    } else if (userMessage.includes("почему не работают некоторые функции?")) {
        return "Функции могут не работать из-за больших на бота. Если какая-то функция не работает, то мы исправляем эту проблему.";
    } else if (userMessage.includes("как найти определенную информацию?")) {
        return "Вся информация находится на нашем сайте.";
    } else if (userMessage.includes("как начать работу с ботом?")) {
        return "Просканируйте QR-код или перейдите по ссылке, которая находится на сайте.";
    } else if (userMessage.includes("требуется ли подключение к интернету?")) {
        return "Да, подключение к интернету обязательное.";
    } else if (userMessage.includes("есть ли ограничения по скорости работы?")) {
        return "Нет, ограничений по скорости работы нету.";
    } else if (userMessage.includes("что умеешь")) {
        return "Я могу отвечать на ваши вопросы и помогать с информацией!";  
    } else {
        return "Извините, я не понимаю. Можете задать другой вопрос?";
    }
}

});