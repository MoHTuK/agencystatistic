document.addEventListener('DOMContentLoaded', function () {
    // ID элементов, к которым вы хотите применить логику
    const ids = ['mailbotButton', 'stopBotButton', 'sendButton'];

    ids.forEach(function(id) {
        const element = document.getElementById(id);
        if (element) {
            element.classList.add('disabled');
            setTimeout(() => {
                element.classList.remove('disabled');
            }, 5000);
        }
    });
});
