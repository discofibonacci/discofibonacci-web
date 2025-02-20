document.addEventListener("DOMContentLoaded", function () {
    const symbolInput = document.getElementById("symbolInput");
    const fetchDataBtn = document.getElementById("fetchData");
    const orderFlowElement = document.getElementById("orderFlow");
    const rsiElement = document.getElementById("rsi");
    const orderBookTable = document.querySelector("#orderBookTable tbody");

    async function fetchMarketData(symbol) {
        try {
            const response = await fetch(`http://127.0.0.1:10000/market-data?symbol=${symbol}`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();

            // Ensure market data elements update correctly
            orderFlowElement.textContent = data.order_flow
                ? `Open: ${data.order_flow.open.toFixed(2)}\nHigh: ${data.order_flow.high.toFixed(2)}\nLow: ${data.order_flow.low.toFixed(2)}\nClose: ${data.order_flow.close.toFixed(2)}\nVolume: ${data.order_flow.volume.toLocaleString()}`
                : "No valid order flow data found.";

            rsiElement.textContent = data.rsi
                ? `RSI: ${data.rsi.toFixed(2)}`
                : "RSI data unavailable.";

        } catch (error) {
            console.error("Error fetching market data:", error);
            orderFlowElement.textContent = "Error fetching order flow.";
            rsiElement.textContent = "Error fetching RSI.";
        }
    }

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
        if (!orderBookTable) return;
        orderBookTable.innerHTML = "";

        data.forEach(order => {
            const row = document.createElement("tr");

            const priceCell = document.createElement("td");
            priceCell.textContent = order.price.toFixed(2);
            priceCell.style.color = order.type === "bid" ? "#00ff00" : "#ff5050";

            const sizeCell = document.createElement("td");
            sizeCell.textContent = order.size.toLocaleString();

            const liquidityCell = document.createElement("td");
            liquidityCell.textContent = order.liquidity.toFixed(2); // Fix empty liquidity column

            row.appendChild(priceCell);
            row.appendChild(sizeCell);
            row.appendChild(liquidityCell);

            orderBookTable.appendChild(row);
        });
    }

    fetchDataBtn.addEventListener("click", function () {
        const symbol = symbolInput.value.trim().toUpperCase() || "AAPL";
        fetchMarketData(symbol);
        fetchMarketDepth(symbol);
    });

    symbolInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            const symbol = symbolInput.value.trim().toUpperCase() || "AAPL";
            fetchMarketData(symbol);
            fetchMarketDepth(symbol);
        }
    });

    // Auto-load default symbol on page load
    fetchMarketData("AAPL");
    fetchMarketDepth("AAPL");
});
