document.addEventListener("DOMContentLoaded", function () {
    let complaintForm = document.querySelector("#complaint-form");

    if (complaintForm) {
        complaintForm.addEventListener("submit", function (event) {
            event.preventDefault();

            let description = document.querySelector("#description").value;
            let location = document.querySelector("#location").value;
            let image = document.querySelector("#image").files[0];

            if (!description || !location) {
                alert("Please fill out all required fields.");
                return;
            }

            let formData = new FormData();
            formData.append("description", description);
            formData.append("location", location);
            if (image) {
                formData.append("image", image);
            }

            fetch("/submit/", {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert("Error: " + data.error);
                } else {
                    alert("Complaint submitted successfully!");
                    window.location.reload();
                }
            })
            .catch(error => console.error("Error:", error));
        });
    }
});

/* Function to Get CSRF Token */
function getCSRFToken() {
    let cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].trim();
        if (cookie.startsWith("csrftoken=")) {
            return cookie.substring("csrftoken=".length, cookie.length);
        }
    }
    return "";
}
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            document.getElementById("latitude").value = position.coords.latitude;
            document.getElementById("longitude").value = position.coords.longitude;
        }, function(error) {
            alert("Error getting location");
        });
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}