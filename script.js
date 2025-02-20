document.addEventListener("DOMContentLoaded", function () {
    const symbolInput = document.getElementById("symbolInput");
    const fetchButton = document.getElementById("fetchData");

    // Allow "Enter" key to trigger data fetch
    symbolInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            fetchMarketData(symbolInput.value.trim().toUpperCase());
            fetchMarketDepth(symbolInput.value.trim().toUpperCase());
        }
    });

    // Button click fetch
    fetchButton.addEventListener("click", function () {
        fetchMarketData(symbolInput.value.trim().toUpperCase());
        fetchMarketDepth(symbolInput.value.trim().toUpperCase());
    });
});

// Fetch Market Data (Price, RSI, Support/Resistance)
async function fetchMarketData(symbol) {
    try {
        const response = await fetch(`http://127.0.0.1:10000/market-data?symbol=${symbol}`);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const data = await response.json();
        console.log("✅ Market Data Fetched:", data); // Debugging Log

        document.getElementById("marketData").innerHTML = `
            <strong>Open:</strong> ${data.order_flow.open.toFixed(2)}  
            <strong>High:</strong> ${data.order_flow.high.toFixed(2)}  
            <strong>Low:</strong> ${data.order_flow.low.toFixed(2)}  
            <strong>Close:</strong> <span style="color: ${data.order_flow.close >= data.order_flow.open ? "limegreen" : "red"}">${data.order_flow.close.toFixed(2)}</span>  
            <strong>Volume:</strong> ${data.order_flow.volume.toLocaleString()}
            <br><br>
            <strong>RSI:</strong> ${data.rsi.toFixed(2)}
        `;

    } catch (error) {
        console.error("❌ Error fetching market data:", error);
        document.getElementById("marketData").innerHTML = "<span style='color: red;'>Failed to load market data.</span>";
    }
}

// Fetch Market Depth (Bid/Ask Order Book)
async function fetchMarketDepth(symbol) {
    try {
        const response = await fetch(`http://127.0.0.1:10000/market-depth?symbol=${symbol}`);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const data = await response.json();
        console.log("📊 Market Depth Data:", data); // Debugging Log

        updateOrderBookTable(data);

    } catch (error) {
        console.error("❌ Error fetching market depth:", error);
    }
}

// Update Market Depth Table (Fix Incorrect Data Display)
function updateOrderBookTable(data) {
    const tableBody = document.querySelector("#orderBookTable tbody");
    tableBody.innerHTML = ""; // Clear previous data

    if (!data || data.length === 0) {
        console.warn("⚠ No market depth data available.");
        tableBody.innerHTML = `<tr><td colspan="3" style="text-align:center; color: red;">No Data</td></tr>`;
        return;
    }

    data.forEach((entry) => {
        const row = document.createElement("tr");

        // Determine color: Green for bids, Red for asks
        let priceColor = entry.type === "bid" ? "limegreen" : "red";

        row.innerHTML = `
            <td style="color:${priceColor}; font-weight:bold">${entry.price.toFixed(2)}</td>
            <td>${entry.size}</td>
            <td>${entry.liquidity.toFixed(2)}</td>
        `;
        tableBody.appendChild(row);
    });
}
