document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-loading-form]").forEach((form) => {
        form.addEventListener("submit", () => {
            const button = form.querySelector("[data-submit-button]");
            if (!button) return;

            button.disabled = true;
            button.textContent = "Creating your plan...";
        });
    });

    document.querySelectorAll('input[type="file"]').forEach((input) => {
        input.addEventListener("change", () => {
            const file = input.files?.[0];
            if (!file) return;

            const maxBytes = 5 * 1024 * 1024;
            if (file.size > maxBytes) {
                window.alert("Please choose an image smaller than 5 MB.");
                input.value = "";
            }
        });
    });
});
