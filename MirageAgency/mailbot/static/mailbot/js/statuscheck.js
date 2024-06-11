$(document).ready(function() {
    // Отложенный запрос на proxy/status спустя 5 секунд после загрузки страницы
    setTimeout(function() {
        checkStatus();
    }, 7000); // 5000 миллисекунд = 5 секунд

    function checkStatus() {
        $.ajax({
            type: 'GET',
            url: 'proxy/status',
            success: function(statusResponse) {
                console.log('Initial status check:', statusResponse);
                // Если статус пустой, это означает, что бот работает
                if (statusResponse && statusResponse.status === "") {
                    $('#mailingStatusIndicator').addClass('green').removeClass('red');
                    $('#mailingStatusText').text('Bot working');
                    // Запуск интервала для повторения запроса каждые 2 минуты, если бот работает
                    var statusCheckInterval = setInterval(function() {
                        $.ajax({
                            type: 'GET',
                            url: 'proxy/status',
                            success: function(response) {
                                console.log('Repeated status check:', response);
                                // Если статус перестает быть пустым, останавливаем интервал
                                if (response && response.status !== "") {
                                    clearInterval(statusCheckInterval);
                                    $('#mailingStatusIndicator').addClass('red').removeClass('green');
                                    $('#mailingStatusText').text('Bot not working');
                                }
                            },
                            error: function() {
                                console.error('Error checking proxy status');
                                clearInterval(statusCheckInterval);
                                $('#mailingStatusIndicator').addClass('red').removeClass('green');
                                $('#mailingStatusText').text('Ошибка проверки статуса');
                            }
                        });
                    }, 120000); // 120000 миллисекунд = 2 минуты
                } else {
                    // Если статус не пустой, бот не работает
                    $('#mailingStatusIndicator').addClass('red').removeClass('green');
                    $('#mailingStatusText').text('Bot not working');
                }
            },
            error: function() {
                console.error('Error checking proxy status');
                $('#mailingStatusIndicator').addClass('red').removeClass('green');
                $('#mailingStatusText').text('Ошибка проверки статуса');
            }
        });
    }
});
