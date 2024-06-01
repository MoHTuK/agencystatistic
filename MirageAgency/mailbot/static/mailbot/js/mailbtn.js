document.addEventListener('DOMContentLoaded', function () {
    const mailbotButton = document.getElementById('mailbotButton');
    if (mailbotButton) {
        mailbotButton.classList.add('disabled');
        setTimeout(() => {
            mailbotButton.classList.remove('disabled');
        }, 5000);
    }
});