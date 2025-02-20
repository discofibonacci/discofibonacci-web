document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("fetchData").addEventListener("click", async function () {
        const symbol = document.getElementById("symbolInput").value || "AAPL";
        try {
            const response = await fetch("http://127.0.0.1:10000/market-data?symbol=AAPL");
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();

            // Check if each key exists before displaying it
            document.getElementById("orderFlow").textContent = data.order_flow 
                ? JSON.stringify(data.order_flow, null, 2) 
                : "No valid order flow data found.";

            document.getElementById("supportLevel").textContent = data.support_level 
                ? data.support_level 
                : "No support level available.";

            document.getElementById("rsi").textContent = (typeof data.rsi === "number" && !isNaN(data.rsi)) 
                ? data.rsi.toFixed(2) 
                : "RSI data unavailable.";

        } catch (error) {
            console.error("Error fetching market data:", error);
            document.getElementById("orderFlow").textContent = "Error fetching order flow.";
            document.getElementById("supportLevel").textContent = "Error fetching support level.";
            document.getElementById("rsi").textContent = "Error fetching RSI.";
        }
    });
});
