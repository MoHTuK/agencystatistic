document.addEventListener('DOMContentLoaded', function () {
    const ids = ['mailbotButton', 'stopBotButton', 'sendButton'];  // ID элементов

    ids.forEach(function(id) {
        const element = document.getElementById(id);
        if (element) {
            element.classList.add('disabled');  // Добавляем класс 'disabled' для деактивации кнопки
            // Устанавливаем различные задержки в зависимости от кнопки
            setTimeout(() => {
                element.classList.remove('disabled');  // Удаляем класс 'disabled' для активации кнопки
            }, id === 'sendButton' ? 10000 : 5000);  // 10 секунд для 'sendButton', 5 секунд для остальных
        }
    });
});
