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
    const latitudeInput = document.getElementById("latitude");
    if (latitudeInput && document.getElementById("get-location-btn")) {
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
    if (footer) {
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
    }

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

    // Chart.js Configuration
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    boxWidth: 12,
                    padding: 15,
                    font: {
                        size: 12
                    }
                }
            }
        },
        layout: {
            padding: {
                top: 5,
                right: 5,
                bottom: 5,
                left: 5
            }
        }
    };

    // Function to resize charts
    function resizeCharts() {
        const isVerySmallScreen = window.innerWidth <= 450;
        const isMobile = window.innerWidth <= 768;
        
        // Only proceed if charts exist
        if (typeof window.complaints7DaysBarChart !== 'undefined' || typeof window.allTimePieChart !== 'undefined') {
            const charts = [
                window.complaints7DaysBarChart, 
                window.allTimePieChart
            ].filter(chart => chart); // Filter out undefined charts
            
            charts.forEach(chart => {
                if (chart && chart.canvas) {
                    const container = chart.canvas.parentElement;
                    if (container) {
                        // Update chart options based on screen size
                        chart.options = {
                            ...chart.options,
                            ...chartOptions,
                            plugins: {
                                ...chartOptions.plugins,
                                legend: {
                                    ...chartOptions.plugins.legend,
                                    position: isVerySmallScreen ? 'bottom' : 'bottom',
                                    labels: {
                                        ...chartOptions.plugins.legend.labels,
                                        boxWidth: isVerySmallScreen ? 8 : (isMobile ? 10 : 12),
                                        padding: isVerySmallScreen ? 8 : (isMobile ? 10 : 15),
                                        font: {
                                            size: isVerySmallScreen ? 9 : (isMobile ? 10 : 12)
                                        }
                                    }
                                }
                            },
                            scales: {
                                x: {
                                    ticks: {
                                        font: {
                                            size: isVerySmallScreen ? 8 : (isMobile ? 10 : 12)
                                        }
                                    }
                                },
                                y: {
                                    ticks: {
                                        font: {
                                            size: isVerySmallScreen ? 8 : (isMobile ? 10 : 12)
                                        }
                                    }
                                }
                            },
                            maintainAspectRatio: false,
                            responsive: true
                        };
                        
                        // Ensure the chart fits within its container
                        chart.resize();
                        chart.update('none'); // Update without animation for better performance
                    }
                }
            });
        }
    }

    // Update chart sizes on window resize with debounce
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(resizeCharts, 250);
    });

    // Handle statistics form
    const statsForm = document.getElementById('statsFilterForm');
    if (statsForm) {
        statsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const filterPeriod = document.getElementById('filterPeriod');
            if (filterPeriod) {
                fetchAndUpdateStatistics(filterPeriod.value);
            }
        });

        // Function to fetch and update statistics
        function fetchAndUpdateStatistics(period) {
            // Disable the form while loading
            const submitButton = statsForm.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Loading...';
            }

            // Show loading state
            document.querySelectorAll('.stat-number').forEach(el => {
                if (el) el.style.opacity = '0.5';
            });

            // Construct the URL with the selected period
            const url = `/api/statistics/?period=${period}`;
            
            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    // Reset opacity
                    document.querySelectorAll('.stat-number').forEach(el => {
                        if (el) el.style.opacity = '1';
                    });

                    // Update statistics with animation
                    animateNumber('reportsCount', data.reports_count || 0);
                    animateNumber('fixedCount', data.fixed_count || 0);
                    animateNumber('updatesCount', data.updates_count || 0);
                })
                .catch(error => {
                    console.error('Error fetching statistics:', error);
                    // Reset opacity and show error state
                    document.querySelectorAll('.stat-number').forEach(el => {
                        if (el) {
                            el.style.opacity = '1';
                            el.style.color = '#ff3333';
                        }
                    });
                })
                .finally(() => {
                    // Re-enable the form
                    if (submitButton) {
                        submitButton.disabled = false;
                        submitButton.textContent = 'Apply';
                    }
                });
        }

        // Initial statistics load if form exists
        const filterPeriod = document.getElementById('filterPeriod');
        if (filterPeriod) {
            fetchAndUpdateStatistics(filterPeriod.value);
        }
    }

    // Function to animate number counting
    function animateNumber(elementId, finalNumber) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const startNumber = parseInt(element.textContent.replace(/,/g, '')) || 0;
        const duration = 1500; // Animation duration in milliseconds
        const steps = 60;
        const increment = (finalNumber - startNumber) / steps;
        let currentStep = 0;

        // Clear any existing animation
        if (element.currentAnimation) {
            clearInterval(element.currentAnimation);
        }

        element.currentAnimation = setInterval(() => {
            currentStep++;
            const currentNumber = Math.round(startNumber + (increment * currentStep));
            element.textContent = currentNumber.toLocaleString();

            if (currentStep >= steps) {
                clearInterval(element.currentAnimation);
                element.textContent = finalNumber.toLocaleString();
                element.currentAnimation = null;
            }
        }, duration / steps);
    }

    // Add hover effect to stat boxes
    document.querySelectorAll('.stat-box').forEach(box => {
        if (box) {
            box.addEventListener('mouseenter', () => {
                box.style.transform = 'translateY(-5px)';
            });
            box.addEventListener('mouseleave', () => {
                box.style.transform = 'translateY(0)';
            });
        }
    });
});

