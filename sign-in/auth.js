document.addEventListener("DOMContentLoaded", () => {
    const allowedDomains = ["student.uwa.edu.au", "uwa.edu.au"];

    function isValidUwaEmail(email) {
        const value = email.trim().toLowerCase();
        const parts = value.split("@");

        if (parts.length !== 2) {
            return false;
        }

        const [localPart, domain] = parts;
        return localPart.length > 0 && allowedDomains.includes(domain);
    }

    function validateUwaEmail(input) {
        const value = input.value.trim();

        if (value === "") {
            input.setCustomValidity("");
            return;
        }

        if (input.validity.typeMismatch) {
            input.setCustomValidity("Please enter a valid email address.");
            return;
        }

        if (!isValidUwaEmail(value)) {
            input.setCustomValidity("Please use an email ending in @student.uwa.edu.au or @uwa.edu.au.");
            return;
        }

        input.setCustomValidity("");
    }

    function validatePasswordMatch(passwordInput, confirmInput) {
        if (!passwordInput || !confirmInput) {
            return;
        }

        if (confirmInput.value === "") {
            confirmInput.setCustomValidity("");
            return;
        }

        if (passwordInput.value !== confirmInput.value) {
            confirmInput.setCustomValidity("Passwords do not match.");
            return;
        }

        confirmInput.setCustomValidity("");
    }

    const emailInputs = document.querySelectorAll('[data-uwa-email="true"]');

    emailInputs.forEach((input) => {
        input.addEventListener("input", () => validateUwaEmail(input));
        input.addEventListener("blur", () => validateUwaEmail(input));
    });

    const signupPassword = document.getElementById("signup-password");
    const signupConfirmPassword = document.getElementById("signup-confirm-password");

    if (signupPassword && signupConfirmPassword) {
        signupPassword.addEventListener("input", () => {
            validatePasswordMatch(signupPassword, signupConfirmPassword);
        });

        signupConfirmPassword.addEventListener("input", () => {
            validatePasswordMatch(signupPassword, signupConfirmPassword);
        });

        signupConfirmPassword.addEventListener("blur", () => {
            validatePasswordMatch(signupPassword, signupConfirmPassword);
        });
    }

    const forms = document.querySelectorAll(".auth-form");

    forms.forEach((form) => {
        form.addEventListener("submit", (event) => {
            const emailInput = form.querySelector('[data-uwa-email="true"]');

            if (emailInput) {
                validateUwaEmail(emailInput);
            }

            if (form.id === "signupForm") {
                validatePasswordMatch(signupPassword, signupConfirmPassword);
            }

            if (!form.checkValidity()) {
                event.preventDefault();
                form.reportValidity();
            }
        });
    });
});