document.addEventListener("DOMContentLoaded", function() {
    console.log("Market Maker Sniper Loaded");

    function sendTestAlert() {
        fetch("https://discofibonacci-web.onrender.com/alert", {
 // Updated URL
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ "message": "Test Alert Triggered!" })
        })
        .then(response => response.json())
        .then(data => console.log("Server Response:", data))
        .catch(error => console.error("Error:", error));
    }

    setTimeout(sendTestAlert, 5000);
});
