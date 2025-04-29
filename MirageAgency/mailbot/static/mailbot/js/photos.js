function checkLimit(checkbox) {
    let checkboxes = document.querySelectorAll('#photos-form input[type="checkbox"]');
    let checkedCount = 0;

    checkboxes.forEach((box) => {
        if (box.checked) checkedCount++;
    });

    if (checkedCount >= 2) {
        checkboxes.forEach((box) => {
            if (!box.checked) {
                box.parentElement.style.display = 'none'; // Скрывает label, который является родителем чекбокса
            }
        });
    } else {
        checkboxes.forEach((box) => {
            box.parentElement.style.display = 'block'; // Показывает все чекбоксы снова, если количество выбранных меньше двух
        });
    }
}