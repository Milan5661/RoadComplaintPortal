document.addEventListener("DOMContentLoaded", function () {
    // Button hover effects
    document.querySelectorAll(".btn").forEach(button => {
        button.addEventListener("mouseenter", () => {
            button.style.transform = "scale(1.1)";
        });
        button.addEventListener("mouseleave", () => {
            button.style.transform = "scale(1)";
        });
    });

    // Highlighting active menu item
    let currentLocation = window.location.pathname;
    document.querySelectorAll(".nav-link").forEach(link => {
        if (link.getAttribute("href") === currentLocation) {
            link.classList.add("active");
        }
    });

    // Fade-in effect for sections
    function revealOnScroll() {
        document.querySelectorAll(".feature, .stat-card").forEach(section => {
            let position = section.getBoundingClientRect().top;
            let screenHeight = window.innerHeight;
            if (position < screenHeight - 100) {
                section.classList.add("fade-in");
            }
        });
    }
    window.addEventListener("scroll", revealOnScroll);
    revealOnScroll();

    // Geolocation for complaint form
    if (document.getElementById("latitude")) {
        document.getElementById("get-location-btn").addEventListener("click", function () {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(position => {
                    document.getElementById("latitude").value = position.coords.latitude;
                    document.getElementById("longitude").value = position.coords.longitude;
                });
            } else {
                alert("Geolocation is not supported by this browser.");
            }
        });
    }
});
