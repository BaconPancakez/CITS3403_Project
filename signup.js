document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('signupForm');
    const passwordInput = document.getElementById('password');
    const passwordRequirements = document.querySelector('.password-requirements');
    
    // Password validation regex patterns
    const patterns = {
        length: /.{8,}/,
        uppercase: /[A-Z]/,
        lowercase: /[a-z]/,
        number: /[0-9]/,
        special: /[!@#$%^&*]/
    };

    // Real-time password validation
    passwordInput.addEventListener('input', function() {
        const password = this.value;
        
        // Show requirements box when user starts typing
        if (password.length > 0) {
            passwordRequirements.classList.add('show');
        } else {
            passwordRequirements.classList.remove('show');
        }

        // Check each requirement
        updateRequirement('req-length', patterns.length.test(password));
        updateRequirement('req-uppercase', patterns.uppercase.test(password));
        updateRequirement('req-lowercase', patterns.lowercase.test(password));
        updateRequirement('req-number', patterns.number.test(password));
        updateRequirement('req-special', patterns.special.test(password));
    });

    function updateRequirement(elementId, isMet) {
        const element = document.getElementById(elementId);
        if (isMet) {
            element.classList.add('met');
        } else {
            element.classList.remove('met');
        }
    }

    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Clear previous errors
        clearAllErrors();
        
        // Validate all fields
        let isValid = true;

        // Full Name validation
        const fullName = document.getElementById('fullName');
        if (!validateFullName(fullName.value)) {
            showError('fullNameError', 'Please enter a valid full name');
            fullName.classList.add('error');
            isValid = false;
        }

        // Email validation
        const email = document.getElementById('email');
        if (!validateEmail(email.value)) {
            showError('emailError', 'Please enter a valid email address');
            email.classList.add('error');
            isValid = false;
        }

        // Password validation
        const password = document.getElementById('password');
        if (!validatePassword(password.value)) {
            showError('passwordError', 'Password does not meet requirements');
            password.classList.add('error');
            isValid = false;
        }

        // Confirm Password validation
        const confirmPassword = document.getElementById('confirmPassword');
        if (password.value !== confirmPassword.value) {
            showError('confirmPasswordError', 'Passwords do not match');
            confirmPassword.classList.add('error');
            isValid = false;
        }

        // Terms validation
        const terms = document.getElementById('terms');
        if (!terms.checked) {
            showError('termsError', 'You must agree to the terms and conditions');
            isValid = false;
        }

        if (isValid) {
            handleFormSubmit(form);
        }
    });

    // Validation functions
    function validateFullName(name) {
        return name.trim().length >= 2;
    }

    function validateEmail(email) {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailPattern.test(email);
    }

    function validatePassword(password) {
        return Object.values(patterns).every(pattern => pattern.test(password));
    }

    function showError(elementId, message) {
        document.getElementById(elementId).textContent = message;
    }

    function clearAllErrors() {
        document.querySelectorAll('.error').forEach(el => {
            el.textContent = '';
        });
        document.querySelectorAll('input').forEach(el => {
            el.classList.remove('error');
        });
    }

    // Handle form submission
    function handleFormSubmit(form) {
        // Collect form data
        const formData = {
            fullName: document.getElementById('fullName').value,
            email: document.getElementById('email').value,
            password: document.getElementById('password').value
        };

        // Here you would typically send this data to a server
        console.log('Form submitted:', formData);
        
        // Show success message
        alert('Account created successfully!\n\nWelcome, ' + formData.fullName);
        
        // Reset form
        form.reset();
        passwordRequirements.classList.remove('show');
        
        // In a real application, you would redirect to login or dashboard
        // window.location.href = '/dashboard';
    }

    // Remove error styling on input
    document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]').forEach(input => {
        input.addEventListener('input', function() {
            if (this.classList.contains('error')) {
                this.classList.remove('error');
                const errorId = this.id + 'Error';
                document.getElementById(errorId).textContent = '';
            }
        });
    });
});
