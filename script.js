// DiscoFibonacci 2.0 - Market Depth Table Integration
document.addEventListener("DOMContentLoaded", function () {
    const symbolInput = document.getElementById("symbolInput");
    const fetchDataBtn = document.getElementById("fetchData");
    const orderBookTable = document.querySelector("#orderBookTable tbody");

    async function fetchMarketDepth(symbol) {
        try {
            const response = await fetch(`http://127.0.0.1:10000/market-depth?symbol=${symbol}`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            updateOrderBookTable(data);
        } catch (error) {
            console.error("Error fetching market depth:", error);
            orderBookTable.innerHTML = "<tr><td colspan='3'>Error fetching data.</td></tr>";
        }
    }

    function updateOrderBookTable(data) {
        if (!orderBookTable) return;  // Prevents errors if the table isn't found
        orderBookTable.innerHTML = "";

        data.forEach(order => {
            const row = document.createElement("tr");

            const priceCell = document.createElement("td");
            priceCell.textContent = order.price.toFixed(2);
            priceCell.style.color = order.type === "bid" ? "#00ff00" : "#ff5050"; // Green for bids, Red for asks

            const sizeCell = document.createElement("td");
            sizeCell.textContent = order.size.toLocaleString();

            const heatmapCell = document.createElement("td");
            heatmapCell.style.backgroundColor = getHeatmapColor(order.liquidity);
            heatmapCell.textContent = "";

            row.appendChild(priceCell);
            row.appendChild(sizeCell);
            row.appendChild(heatmapCell);

            orderBookTable.appendChild(row);
        });
    }

    function getHeatmapColor(liquidity) {
        const intensity = Math.min(255, Math.floor(liquidity * 2.5));
        return `rgba(255, 165, 0, ${intensity / 255})`;
    }

    fetchDataBtn.addEventListener("click", function () {
        fetchMarketDepth(symbolInput.value || "AAPL");
    });

    symbolInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            fetchMarketDepth(symbolInput.value || "AAPL");
        }
    });
});
