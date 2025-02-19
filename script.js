document.addEventListener("DOMContentLoaded", function () {
    const API_BASE_URL = "https://discofibonacci-web.onrender.com"; // Ensure this is the correct Render API URL

    document.getElementById("fetchData").addEventListener("click", async function () {
        const symbol = document.getElementById("symbolInput").value || "AAPL";

        try {
            const response = await fetch(`${API_BASE_URL}/market-data?symbol=${symbol}`);

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();

            document.getElementById("orderFlow").textContent = JSON.stringify(data.order_flow, null, 2);
            document.getElementById("supportLevel").textContent = data.support_level;
            document.getElementById("rsi").textContent = data.rsi.toFixed(2);
        } catch (error) {
            console.error("Error fetching market data:", error);
            document.getElementById("orderFlow").textContent = "Error loading data";
            document.getElementById("supportLevel").textContent = "Error";
            document.getElementById("rsi").textContent = "Error";
        }
    });
});
