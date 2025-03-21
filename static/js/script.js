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

    // Handle footer visibility
    const footer = document.querySelector('.footer');
    let lastScrollY = window.scrollY;
    let ticking = false;

    function updateFooterVisibility() {
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
        const scrolledToBottom = (window.scrollY + windowHeight) >= (documentHeight - 10);

        if (scrolledToBottom) {
            footer.classList.add('visible');
        } else {
            footer.classList.remove('visible');
        }
        
        ticking = false;
    }

    window.addEventListener('scroll', function() {
        lastScrollY = window.scrollY;
        if (!ticking) {
            window.requestAnimationFrame(function() {
                updateFooterVisibility();
                ticking = false;
            });
            ticking = true;
        }
    });

    // Initial check
    updateFooterVisibility();

    // Get user's location
    const getLocationBtn = document.getElementById('getLocationBtn');
    if (getLocationBtn) {
        getLocationBtn.addEventListener('click', function() {
            if (navigator.geolocation) {
                getLocationBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Getting Location...';
                navigator.geolocation.getCurrentPosition(function(position) {
                    document.getElementById('latitude').value = position.coords.latitude;
                    document.getElementById('longitude').value = position.coords.longitude;
                    getLocationBtn.innerHTML = '<i class="fas fa-map-marker-alt"></i> Location Updated';
                    getLocationBtn.classList.add('success');
                }, function(error) {
                    getLocationBtn.innerHTML = '<i class="fas fa-exclamation-circle"></i> Location Error';
                    getLocationBtn.classList.add('error');
                    console.error('Error getting location:', error);
                });
            } else {
                getLocationBtn.innerHTML = '<i class="fas fa-exclamation-circle"></i> Not Supported';
                getLocationBtn.classList.add('error');
            }
        });
    }
});
