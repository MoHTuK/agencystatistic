document.addEventListener('DOMContentLoaded', function() {
    var selectElement = document.getElementById('recipient_group');
    var additionalTextarea = document.getElementById('additional_textarea');

    selectElement.addEventListener('change', function() {
        // Проверяем, выбрана ли опция "Custom list"
        if (this.value === 'custom_list') {
            additionalTextarea.style.display = 'block'; // Показываем дополнительную textarea
        } else {
            additionalTextarea.style.display = 'none'; // Скрываем дополнительную textarea
        }
    });
});