document.addEventListener("DOMContentLoaded", function () {
    const symbolInput = document.getElementById("symbolInput");
    const fetchDataBtn = document.getElementById("fetchData");
    const orderFlowElement = document.getElementById("orderFlow");
    const rsiElement = document.getElementById("rsi");
    const supportLevelsElement = document.getElementById("supportLevels");
    const resistanceLevelsElement = document.getElementById("resistanceLevels");
    const orderBookTable = document.querySelector("#orderBookTable tbody");

    let lastClose = null; // Store last close price for color change

    async function fetchMarketData(symbol) {
        try {
            const response = await fetch(`http://127.0.0.1:10000/market-data?symbol=${symbol}`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();

            console.log("Market Data Fetched:", data);

            if (!orderFlowElement || !rsiElement || !supportLevelsElement || !resistanceLevelsElement) {
                console.error("Market Data Elements Not Found in DOM");
                return;
            }

            if (!data.order_flow) {
                orderFlowElement.innerHTML = "<b>No valid order flow data found.</b>";
                return;
            }

            let closeColor = data.order_flow.close > data.order_flow.open ? "#00ff00" : "#ff5050";

            orderFlowElement.innerHTML = `
                <b>Open:</b> ${data.order_flow.open.toFixed(2)}<br>
                <b>High:</b> ${data.order_flow.high.toFixed(2)}<br>
                <b>Low:</b> ${data.order_flow.low.toFixed(2)}<br>
                <b>Close:</b> <span style="color:${closeColor}">${data.order_flow.close.toFixed(2)}</span><br>
                <b>Volume:</b> ${data.order_flow.volume.toLocaleString()}
            `;

            rsiElement.innerHTML = `<b>RSI:</b> ${data.rsi ? data.rsi.toFixed(2) : "Unavailable"}`;

            // Handle support & resistance levels
            supportLevelsElement.innerHTML = data.support_level
                ? `<b>Support Levels:</b> ${data.support_level.split(", ").map(level => `<br>S: ${level}`).join("")}`
                : "<b>Support Levels:</b> No data available.";

            resistanceLevelsElement.innerHTML = data.resistance_level
                ? `<b>Resistance Levels:</b> ${data.resistance_level.split(", ").map(level => `<br>R: ${level}`).join("")}`
                : "<b>Resistance Levels:</b> No data available.";

        } catch (error) {
            console.error("Error fetching market data:", error);
            if (orderFlowElement) orderFlowElement.innerHTML = "<b>Error fetching order flow.</b>";
            if (rsiElement) rsiElement.innerHTML = "<b>Error fetching RSI.</b>";
        }
    }

    async function fetchMarketDepth(symbol) {
        console.log(`Fetching Market Depth for: ${symbol}`); // Debugging log
        try {
            const response = await fetch(`http://127.0.0.1:10000/market-depth?symbol=${symbol}`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            console.log("Market Depth Data Fetched:", data); // Debugging log
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
            liquidityCell.textContent = order.liquidity.toFixed(2);

            row.appendChild(priceCell);
            row.appendChild(sizeCell);
            row.appendChild(liquidityCell);

            orderBookTable.appendChild(row);
        });
    }

    function triggerDataFetch() {
        const symbol = symbolInput.value.trim().toUpperCase() || "AAPL";
        fetchMarketData(symbol);
        fetchMarketDepth(symbol);
    }

    fetchDataBtn.addEventListener("click", triggerDataFetch);

    symbolInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            triggerDataFetch();
        }
    });

    // Auto-load default symbol on page load
    triggerDataFetch();
});
