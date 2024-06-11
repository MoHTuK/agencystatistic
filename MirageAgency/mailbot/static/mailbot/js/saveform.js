$(document).ready(function() {

    // Обработка отправки формы Blacklist
    $('.blacklist-form').on('submit', function(e) {
        e.preventDefault(); // Предотвращение стандартной отправки формы
        var form = this; // Сохранение ссылки на форму
        var formData = $(form).serialize(); // Сериализация данных формы

        $.ajax({
            type: 'POST',
            url: 'proxy/save_to_blacklist',
            data: formData,
            success: function(response) {
                if (response.success) {
                     console.log(response); // Выведет в консоль всё, что вернул сервер
                    alert(response.message);
                    $(form).find("input[type=number]").val(""); // Очистка поля ввода после успешной отправки
                } else {
                    alert(response.message);
                    $(form).find("input[type=number]").val(""); // Очистка поля ввода после успешной отправки
                }
            },
            error: function() {
                alert('Error processing your request');
            }
        });
    });

    // Обработка отправки формы Goldman
    $('.goldman-form').on('submit', function(e) {
        e.preventDefault(); // Предотвращение стандартной отправки формы
        var form = this; // Сохранение ссылки на форму
        var formData = $(form).serialize(); // Сериализация данных формы

        $.ajax({
            type: 'POST',
            url: 'proxy/save_to_goldman',
            data: formData,
            success: function(response) {
                if (response.success) {
                    alert(response.message);
                    $(form).find("input[type=number]").val(""); // Очистка поля ввода после успешной отправки
                } else {
                    alert(response.message);
                    $(form).find("input[type=number]").val(""); // Очистка поля ввода после успешной отправки
                }
            },
            error: function() {
                alert('Error processing your request');
            }
        });
    });

    var statusCheckInterval;  // Переменная для хранения интервала
    var lastRequestTime = 0;  // Время последнего запроса
    var requestDelay = 6000;  // Минимальное время задержки между запросами в миллисекундах
    var shouldContinueMailing = false;  // Флаг для контроля продолжения рассылки

    function canMakeRequest() {
        var currentTime = new Date().getTime();
        return (currentTime - lastRequestTime) >= requestDelay;
    }

    function updateLastRequestTime() {
        lastRequestTime = new Date().getTime();
    }

    function toggleFormElements(disabled) {
        $('#recipient_group').prop('disabled', disabled);
        $('.mailbot_textarea').prop('readonly', disabled);
        $('input[type=checkbox]').prop('disabled', disabled);  // Если есть чекбоксы для вложений или других параметров
    }

    // Функция для отправки сообщений
    function sendMessages() {

        if (canMakeRequest() === false) {
            console.log('Waiting to make the next request' + (new Date().getTime() - lastRequestTime));
            setTimeout(sendMessages, requestDelay - (new Date().getTime() - lastRequestTime));
            return;
        }

        var formData = $('.pre_sending-form').serialize(); // Получаем данные из формы
        $.ajax({
            type: 'POST',
            url: 'proxy/send_msg',
            data: formData,
             beforeSend: function() {
                updateLastRequestTime();  // Обновляем время последнего запроса перед выполнением запроса
                if ($('#recipient_group').val() === 'online_men') {
                    toggleFormElements(true);  // Блокируем элементы формы
                }
            },
            success: function(response) {
                if (response.success) {
                    console.log(response); // Вывод в консоль всего, что вернул сервер
                    $('#mailingStatusIndicator').addClass('green').removeClass('red');
                    $('#mailingStatusText').text('Bot working');
                    startStatusCheck();

                } else {
                    alert(response.message);
                    $('#mailingStatusIndicator').addClass('red').removeClass('green');
                    $('#mailingStatusText').text('Bot not working');
                }
            },
            error: function() {
                alert('Error processing your request');
                $('#mailingStatusIndicator').addClass('red').removeClass('green');
                $('#mailingStatusText').text('Ошибка обработки запроса');
            }
        });
    }

    function checkStatus() {

        if (canMakeRequest() === false) {
            console.log('Waiting to make the next request' + (new Date().getTime() - lastRequestTime));
            setTimeout(checkStatus, requestDelay - (new Date().getTime() - lastRequestTime));
            return;
        }


        $.ajax({
            type: 'GET',
            url: 'proxy/status',
            beforeSend: function() {
                updateLastRequestTime();  // Обновляем время последнего запроса перед выполнением запроса
            },
            success: function(statusResponse) {
                if (statusResponse && statusResponse.status) {
                    if (['end', 'limit', 'Stop'].includes(statusResponse.status)) {
                        clearInterval(statusCheckInterval);
                        $('#mailingStatusIndicator').addClass('red').removeClass('green');
                        $('#mailingStatusText').text('Bot not working');
                        console.log('Stop work');
                        if ($('#recipient_group').val() === 'online_men' && shouldContinueMailing) {

                            $('#mailingStatusIndicator').addClass('green').removeClass('red');
                            $('#mailingStatusText').text('Bot working');
                            $('#recipient_group').prop('disabled', false);
                            $('.mailbot_textarea').prop('readonly', false);
                            $('input[type=checkbox]').prop('disabled', false);  // Если есть чекбоксы для вложений или других параметров

                            console.log('Status ended and Men Online is selected. Planning to restart mailing in 5 seconds.');
                            sendMessages()
                        }
                    }
                } else {
                    $('#mailingStatusIndicator').addClass('green').removeClass('red');
                    $('#mailingStatusText').text('Bot working');
                    console.log('Received an empty or invalid status response.');
                }
            },
            error: function() {
                console.error('Error checking proxy status');
                $('#mailingStatusText').text('Trying to check status again');
                checkStatus()
            }
        });
    }

    function startStatusCheck() {
        if (statusCheckInterval) {
            clearInterval(statusCheckInterval);
        }
        statusCheckInterval = setInterval(checkStatus, 120000); // Повтор каждые 2 минуты
    }


    function stopBot() {

        if (canMakeRequest() === false) {
            console.log('Waiting to make the next request' + (new Date().getTime() - lastRequestTime));
            setTimeout(stopBot, requestDelay - (new Date().getTime() - lastRequestTime));
            return;
        }

        $.ajax({
            type: 'GET',
            url: 'proxy/stop',
            beforeSend: function() {
                updateLastRequestTime();  // Обновляем время последнего запроса
            },
            success: function(response) {
                console.log('Bot stop response:', response);
                if (response.success) {
                    clearInterval(statusCheckInterval);  // Останавливаем проверку статуса
                    $('#mailingStatusIndicator').addClass('red').removeClass('green');
                    $('#mailingStatusText').text('Bot stopped');
                    shouldContinueMailing = false;  // Обновляем флаг, чтобы остановить рассылку
                    toggleFormElements(false);  // Разблокируем все элементы формы
                    alert('Bot stopped successfully');
                } else {
                    alert('Failed to stop the bot: ' + response.status);
                }
            },
            error: function() {
                alert('Error stopping the bot');
            }
        });
    }

    // Обработка отправки формы
    $('.pre_sending-form').on('submit', function(e) {
        e.preventDefault();
        shouldContinueMailing = true;  // Сбрасываем флаг при новой отправке
        $('#recipient_group').prop('disabled', false);
        $('.mailbot_textarea').prop('readonly', false);
        $('input[type=checkbox]').prop('disabled', false);
        sendMessages();
        alert("Рассылка запущена успешно");
    });

     // Обработчик для кнопки остановки бота
    $('#stopBotButton').on('click', function() {
        stopBot();
    });
});
