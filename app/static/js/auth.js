document.addEventListener("DOMContentLoaded", () => {
    const uwaEmailPattern = /^[^\s@]+@(student\.uwa\.edu\.au|uwa\.edu\.au)$/i;

    function validateUwaEmail(input) {
        const value = input.value.trim();

        if (value === "") {
            input.setCustomValidity("");
            return true;
        }

        if (input.validity.typeMismatch) {
            input.setCustomValidity("Please enter a valid email address.");
            return false;
        }

        if (!uwaEmailPattern.test(value)) {
            input.setCustomValidity("Please use an email ending in @student.uwa.edu.au or @uwa.edu.au.");
            return false;
        }

        input.setCustomValidity("");
        return true;
    }

    function validatePasswordLength(form) {
        const passwordInput = form.querySelector('[data-password="true"]');
        const confirmInput = form.querySelector('[data-confirm-password="true"]');
        if (!passwordInput || !confirmInput) {
            return true;
        }

        const value = passwordInput.value;
        if (value.length === 0) {
            passwordInput.setCustomValidity("");
            return true;
        }

        if (value.length < 8) {
            passwordInput.setCustomValidity(
                "Password must be at least 8 characters."
            );
            return false;
        }

        passwordInput.setCustomValidity("");
        return true;
    }

    function validatePasswordMatch(form) {
        const passwordInput = form.querySelector('[data-password="true"]');
        const confirmInput = form.querySelector('[data-confirm-password="true"]');

        if (!passwordInput || !confirmInput) {
            return true;
        }

        if (confirmInput.value === "") {
            confirmInput.setCustomValidity("");
            return true;
        }

        if (passwordInput.value !== confirmInput.value) {
            confirmInput.setCustomValidity("Passwords do not match.");
            return false;
        }

        confirmInput.setCustomValidity("");
        return true;
    }

    document.querySelectorAll('[data-uwa-email="true"]').forEach((input) => {
        input.addEventListener("input", () => validateUwaEmail(input));
        input.addEventListener("blur", () => validateUwaEmail(input));
    });

    document.querySelectorAll(".auth-form").forEach((form) => {
        const passwordInput = form.querySelector('[data-password="true"]');
        const confirmInput = form.querySelector('[data-confirm-password="true"]');

        if (passwordInput && confirmInput) {
            passwordInput.addEventListener("input", () => {
                validatePasswordLength(form);
                validatePasswordMatch(form);
            });
            passwordInput.addEventListener("blur", () => {
                validatePasswordLength(form);
                validatePasswordMatch(form);
            });
            confirmInput.addEventListener("input", () => {
                validatePasswordLength(form);
                validatePasswordMatch(form);
            });
            confirmInput.addEventListener("blur", () => {
                validatePasswordLength(form);
                validatePasswordMatch(form);
            });
        }

        form.addEventListener("submit", (event) => {
            const emailInput = form.querySelector('[data-uwa-email="true"]');
            const emailValid = emailInput ? validateUwaEmail(emailInput) : true;
            const passwordLengthValid = validatePasswordLength(form);
            const passwordMatchValid = validatePasswordMatch(form);

            if (
                !emailValid ||
                !passwordLengthValid ||
                !passwordMatchValid ||
                !form.checkValidity()
            ) {
                event.preventDefault();
                form.reportValidity();
            }
        });
    });
});