document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("fetchData").addEventListener("click", async function () {
        const symbol = document.getElementById("symbolInput").value || "AAPL";
        try {
            const response = await fetch(`https://discofibonacci-web.onrender.com/market-data?symbol=${symbol}`);
            const data = await response.json();
            
            document.getElementById("orderFlow").textContent = JSON.stringify(data.order_flow, null, 2);
            document.getElementById("supportLevel").textContent = data.support_level;
            document.getElementById("rsi").textContent = isNaN(data.rsi) ? "Error" : data.rsi.toFixed(2);
        } catch (error) {
            console.error("Error fetching market data:", error);
            document.getElementById("orderFlow").textContent = "Error loading data";
            document.getElementById("supportLevel").textContent = "Error";
            document.getElementById("rsi").textContent = "Error";
        }
    });
});
