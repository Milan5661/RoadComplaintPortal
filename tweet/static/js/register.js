document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("register-form");

    form.addEventListener("submit", function (event) {
        const username = form.querySelector("#id_username").value.trim();
        const password1 = form.querySelector("#id_password1").value.trim();
        const password2 = form.querySelector("#id_password2").value.trim();
        const usernamePattern = /^[a-zA-Z0-9_]{4,15}$/; // Username: 4-15 alphanumeric chars
        const passwordPattern = /^[a-zA-Z0-9]{8,15}$/; // Password: 8-15 alphanumeric chars

        if (!usernamePattern.test(username)) {
            alert("Username must be 4-15 characters long and contain only letters, numbers, or underscores.");
            event.preventDefault();
            return;
        }

        if (!passwordPattern.test(password1)) {
            alert("Password must be 8-15 characters long and contain only letters and numbers.");
            event.preventDefault();
            return;
        }

        if (password1 !== password2) {
            alert("Passwords do not match!");
            event.preventDefault();
            return;
        }
    });
});
