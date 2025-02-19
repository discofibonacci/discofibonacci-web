document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("fetchData").addEventListener("click", async function () {
        const symbol = document.getElementById("symbolInput").value || "AAPL";
        const response = await fetch(`/market-data?symbol=${symbol}`);
        const data = await response.json();

        document.getElementById("orderFlow").textContent = JSON.stringify(data.order_flow, null, 2);
        document.getElementById("supportLevel").textContent = data.support_level;
        document.getElementById("rsi").textContent = data.rsi.toFixed(2);
    });
});
