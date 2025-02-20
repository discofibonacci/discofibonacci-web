document.addEventListener("DOMContentLoaded", function () {
    const symbolInput = document.getElementById("symbolInput");
    const fetchDataBtn = document.getElementById("fetchData");
    const orderFlowElement = document.getElementById("orderFlow");
    const rsiElement = document.getElementById("rsi");
    const supportElement = document.getElementById("supportLevels");
    const resistanceElement = document.getElementById("resistanceLevels");
    const orderBookTable = document.querySelector("#orderBookTable tbody");

    let lastClose = null; // Store last close price for color change

    async function fetchMarketData(symbol) {
        try {
            console.log(`Fetching Market Data for: ${symbol}`);
            const response = await fetch(`http://127.0.0.1:10000/market-data?symbol=${symbol}`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            console.log("Market Data Fetched:", data);

            if (!data.order_flow) {
                orderFlowElement.innerHTML = "<b>No valid order flow data found.</b>";
                return;
            }

            let closeColor = "white";
            if (lastClose !== null) {
                closeColor = data.order_flow.close > lastClose ? "#00ff00" : "#ff5050";
            }
            lastClose = data.order_flow.close;

            orderFlowElement.innerHTML = `
                <b>Open:</b> ${data.order_flow.open.toFixed(2)}<br>
                <b>High:</b> ${data.order_flow.high.toFixed(2)}<br>
                <b>Low:</b> ${data.order_flow.low.toFixed(2)}<br>
                <b>Close:</b> <span style="color:${closeColor}">${data.order_flow.close.toFixed(2)}</span><br>
                <b>Volume:</b> ${data.order_flow.volume.toLocaleString()}
            `;

            rsiElement.innerHTML = `<b>RSI:</b> ${data.rsi ? data.rsi.toFixed(2) : "Unavailable"}`;

            // Ensure support and resistance levels are displayed correctly
            supportElement.innerHTML = `<b>Support Levels:</b><br> ${
                Array.isArray(data.support_level) 
                    ? data.support_level.map(s => `S: ${s}`).join("<br>")
                    : data.support_level.split(',').map(s => `S: ${s.trim()}`).join("<br>")
            }`;

            resistanceElement.innerHTML = `<b>Resistance Levels:</b><br> ${
                Array.isArray(data.resistance_level) 
                    ? data.resistance_level.map(r => `R: ${r}`).join("<br>")
                    : data.resistance_level.split(',').map(r => `R: ${r.trim()}`).join("<br>")
            }`;

        } catch (error) {
            console.error("Error fetching market data:", error);
            orderFlowElement.innerHTML = "<b>Error fetching order flow.</b>";
            rsiElement.innerHTML = "<b>Error fetching RSI.</b>";
            supportElement.innerHTML = "<b>Support Levels:</b> Loading...";
            resistanceElement.innerHTML = "<b>Resistance Levels:</b> Loading...";
        }
    }

    async function fetchMarketDepth(symbol) {
        try {
            console.log(`Fetching Market Depth for: ${symbol}`);
            const response = await fetch(`http://127.0.0.1:10000/market-depth?symbol=${symbol}`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            console.log("Market Depth Data:", data);
            updateOrderBookTable(data);
        } catch (error) {
            console.error("Error fetching market depth:", error);
            orderBookTable.innerHTML = "<tr><td colspan='3'>Error fetching data.</td></tr>";
        }
    }

    function updateOrderBookTable(data) {
        if (!orderBookTable) return;
        orderBookTable.innerHTML = ""; // Clears old data before inserting new

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
        const symbol = symbolInput.value.trim().toUpperCase();
        if (!symbol) {
            console.log("No symbol entered. Data fetch skipped.");
            return;
        }
        console.log(`Fetching Data for Symbol: ${symbol}`);
        fetchMarketData(symbol);
        fetchMarketDepth(symbol);
    }

    fetchDataBtn.addEventListener("click", triggerDataFetch);
    symbolInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            triggerDataFetch();
        }
    });

});
