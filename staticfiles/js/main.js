document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript Loaded!");

    const menuToggle = document.getElementById("menu-toggle");
    if (menuToggle) {
        menuToggle.addEventListener("click", function () {
            const menu = document.getElementById("menu");
            if (menu) {
                menu.classList.toggle("active");
            }
        });
    }
});
