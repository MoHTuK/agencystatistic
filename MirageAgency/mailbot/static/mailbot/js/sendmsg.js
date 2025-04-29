function getManIdListAndSendMail() {
    fetch("proxy/onlineman", {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        const manIdList = data; // Предполагаем, что data уже является списком ID
        sendMail(manIdList);
    })
    .catch(error => console.error('Ошибка получения списка ID:', error));
}

function sendMail(manIdList) {
    var messageText = document.getElementById('messageText').value;
    var attachments = document.querySelectorAll('.attachment:checked');
    var attachIds = Array.from(attachments).map(input => input.value);

    // Создание строки запроса с параметрами
    var queryParams = new URLSearchParams({
        text: messageText,
        attach_id1: attachIds[0] || '',
        attach_id2: attachIds[1] || '',
        man_id_list: manIdList.join(','), // Преобразование списка ID в строку, разделенную запятыми
    }).toString();

    fetch(`proxy/send_msg`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Ошибка отправки письма:', error));
}

document.getElementById('sendButton').addEventListener('click', getManIdListAndSendMail);
