document.addEventListener("DOMContentLoaded", () => {
    // Мобильное меню
    const toggle = document.querySelector(".nav-toggle");
    const navigation = document.querySelector(".main-nav");

    if (toggle && navigation) {
        toggle.addEventListener("click", () => {
            const isOpen = navigation.classList.toggle("open");

            toggle.setAttribute(
                "aria-expanded",
                String(isOpen)
            );

            toggle.textContent = isOpen ? "×" : "☰";
        });
    }

    // Закрытие уведомлений
    const messageButtons = document.querySelectorAll(
        ".message button"
    );

    messageButtons.forEach((button) => {
        button.addEventListener("click", () => {
            button.parentElement.remove();
        });
    });

    // Автоматическое скрытие уведомлений
    window.setTimeout(() => {
        const messages = document.querySelectorAll(".message");

        messages.forEach((message) => {
            message.remove();
        });
    }, 5000);

    // Переключение доставки и самовывоза
    const deliveryInputs = document.querySelectorAll(
        'input[name="delivery_type"]'
    );

    const addressFields = document.querySelector(
        "#address-fields"
    );

    function syncAddressFields() {
        if (!addressFields) {
            return;
        }

        const selectedDelivery = document.querySelector(
            'input[name="delivery_type"]:checked'
        );

        const isPickup =
            selectedDelivery &&
            selectedDelivery.value === "pickup";

        addressFields.hidden = Boolean(isPickup);
    }

    deliveryInputs.forEach((input) => {
        input.addEventListener(
            "change",
            syncAddressFields
        );
    });

    syncAddressFields();
});

