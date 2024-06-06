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

    $('.pre_sending-form').on('submit', function(e) {
        e.preventDefault(); // Предотвращение стандартной отправки формы
        var form = this; // Сохранение ссылки на форму
        var formData = $(form).serialize(); // Сериализация данных формы


        $.ajax({
            type: 'POST',
            url: 'proxy/send_msg',
            data: formData,
            success: function(response) {
                if (response.success) {
                    console.log(response); // Выведет в консоль всё, что вернул сервер
                    alert(response.message);
                    $('#mailingStatusIndicator').addClass('green').removeClass('red');  // Сделать индикатор зеленым
                    $('#mailingStatusText').text('Bot working');  // Обновить текст статуса


                    var statusCheckInterval = setInterval(function() {
                        $.ajax({
                            type: 'GET',
                            url: 'proxy/status',
                            success: function(statusResponse) {
                                // Проверяем, не пустой ли ответ и содержит ли ключ 'status'
                                if (statusResponse && statusResponse.status) {
                                    if (['end', 'limit', 'Stop'].includes(statusResponse.status)) {
                                        clearInterval(statusCheckInterval);
                                        $('#mailingStatusIndicator').addClass('red').removeClass('green');  // Сменить на красный
                                        $('#mailingStatusText').text('Bot not working');  // Обновить текст статуса
                                        console.log(`Status check ended because the status is '${statusResponse.status}'.`);
                                    }
                                } else {
                                    // Если ответ пустой, логируем это и продолжаем проверки
                                    console.log('Received an empty or invalid status response.');
                                    $('#mailingStatusIndicator').addClass('green').removeClass('red');  // Сделать индикатор зеленым
                                    $('#mailingStatusText').text('Bot working');  // Обновить текст статуса
                                }
                            },
                            error: function() {
                                console.error('Error checking proxy status');
                                 $('#mailingStatusIndicator').addClass('red').removeClass('green');  // В случае ошибки также сменить на красный
                                 $('#mailingStatusText').text('Ошибка проверки статуса');  // Обновить текст статуса
                            }
                        });
                    }, 120000);
                } else {
                    alert(response.message);
                    $('#mailingStatusIndicator').addClass('red').removeClass('green');  // Сменить на красный если отправка не успешна
                    $('#mailingStatusText').text('Bot not working');  // Обновить текст статуса
                }
            },
            error: function() {
                alert('Error processing your request');
                $('#mailingStatusIndicator').addClass('red').removeClass('green');  // Сменить на красный в случае ошибки AJAX
                $('#mailingStatusText').text('Ошибка обработки запроса');  // Обновить текст статуса
            }
        });
    });
});
