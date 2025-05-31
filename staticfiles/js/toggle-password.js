// toggle-password.js
// Handles show/hide password fields with eye icon for all forms

document.addEventListener('DOMContentLoaded', function() {
    // Registration & Login
    const passwordInput = document.getElementById('password');
    const togglePassword = document.getElementById('togglePassword');
    if (passwordInput && togglePassword) {
        togglePassword.addEventListener('change', function () {
            passwordInput.type = this.checked ? 'text' : 'password';
        });
    }
    // Registration
    const confirmPasswordInput = document.getElementById('confirm_password');
    const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');
    if (confirmPasswordInput && toggleConfirmPassword) {
        toggleConfirmPassword.addEventListener('change', function () {
            confirmPasswordInput.type = this.checked ? 'text' : 'password';
        });
    }
    // Password Reset (admin/user)
    const newPasswordInput = document.getElementById('id_new_password');
    const toggleNewPassword = document.getElementById('toggleNewPassword');
    if (newPasswordInput && toggleNewPassword) {
        toggleNewPassword.addEventListener('change', function () {
            newPasswordInput.type = this.checked ? 'text' : 'password';
        });
    }
    const resetConfirmPasswordInput = document.getElementById('id_confirm_password');
    if (resetConfirmPasswordInput && toggleConfirmPassword) {
        toggleConfirmPassword.addEventListener('change', function () {
            resetConfirmPasswordInput.type = this.checked ? 'text' : 'password';
        });
    }
    // Admin login
    const adminPasswordInput = document.getElementById('id_password');
    const toggleAdminPassword = document.getElementById('toggleAdminPassword');
    if (adminPasswordInput && toggleAdminPassword) {
        toggleAdminPassword.addEventListener('change', function () {
            adminPasswordInput.type = this.checked ? 'text' : 'password';
        });
    }
});
