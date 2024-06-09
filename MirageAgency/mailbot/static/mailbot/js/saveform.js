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

    var shouldContinueMailing = false;  // Флаг для контроля продолжения рассылки

    function toggleFormElements(disabled) {
        $('#recipient_group').prop('disabled', disabled);
        $('.mailbot_textarea').prop('readonly', disabled);
        $('input[type=checkbox]').prop('disabled', disabled);  // Если есть чекбоксы для вложений или других параметров
    }

    // Функция для отправки сообщений
    function sendMessages() {
        var formData = $('.pre_sending-form').serialize(); // Получаем данные из формы
        $.ajax({
            type: 'POST',
            url: 'proxy/send_msg',
            data: formData,
             beforeSend: function() {
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

    // Начать проверку статуса
    function startStatusCheck() {
        if (statusCheckInterval) {
            clearInterval(statusCheckInterval);  // Очищаем существующий интервал перед созданием нового
        }
        var statusCheckInterval = setInterval(function() {
            $.ajax({
                type: 'GET',
                url: 'proxy/status',
                success: function(statusResponse) {
                    if (statusResponse && statusResponse.status) {
                        if (['end', 'limit', 'Stop'].includes(statusResponse.status)) {
                            clearInterval(statusCheckInterval);
                            $('#mailingStatusIndicator').addClass('red').removeClass('green');
                            $('#mailingStatusText').text('Bot not working');
                            console.log('Stop work');
                            // Автоматический перезапуск, если выбрано 'Men Online'
                            if ($('#recipient_group').val() === 'online_men' && shouldContinueMailing) {
                                $('#mailingStatusIndicator').addClass('green').removeClass('red');
                                $('#mailingStatusText').text('Bot working');
                                $('#recipient_group').prop('disabled', false);
                                $('.mailbot_textarea').prop('readonly', false);
                                $('input[type=checkbox]').prop('disabled', false);  // Если есть чекбоксы для вложений или других параметров
                                console.log('Status ended and Men Online is selected. Planning to restart mailing in 5 seconds.');
                                setTimeout(function() {  // Задержка перед повторным запуском
                                    sendMessages();
                                }, 10000);
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
                    $('#mailingStatusIndicator').addClass('red').removeClass('green');
                    $('#mailingStatusText').text('Пробую проверить еще 1 раз');
                    setTimeout(startStatusCheck, 5000);  // Попытка повторной проверки через 5 секунд
                    clearInterval(statusCheckInterval);  // Очищаем существующий интервал перед созданием нового
                }
            });
        }, 120000);
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
        $.ajax({
            type: 'GET',
            url: 'proxy/stop',
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
    });
});
