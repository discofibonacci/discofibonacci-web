document.addEventListener("DOMContentLoaded", function () {
    const symbolInput = document.getElementById("symbolInput");
    const fetchDataBtn = document.getElementById("fetchData");
    const orderFlowElement = document.getElementById("orderFlow");
    const rsiElement = document.getElementById("rsi");
    const supportElement = document.getElementById("supportLevels");
    const resistanceElement = document.getElementById("resistanceLevels");
    const vwapElement = document.getElementById("vwap");
    const orderBookTable = document.querySelector("#orderBookTable tbody");
    const priceChartCanvas = document.getElementById("priceChart");

    let lastClose = null;
    let priceChart = null;

    // Register Candlestick Chart Type
    Chart.register(
        CandlestickController,
        CandlestickElement,
        OhlcController,
        OhlcElement
    );
    

    function updatePriceChart(data) {
        console.log("Updating Price Chart with:", data);

        if (!data.candlesticks || data.candlesticks.length === 0) {
            console.error("No valid candlestick data available for the chart.");
            return;
        }

        const ctx = priceChartCanvas.getContext("2d");

        // Convert API data into candlestick format
        const candlestickData = data.candlesticks.map(entry => ({
            x: new Date(entry.time),
            o: entry.open,
            h: entry.high,
            l: entry.low,
            c: entry.close
        }));

        const config = {
            type: "candlestick",
            data: {
                datasets: [{
                    label: "Price Movement",
                    data: candlestickData,
                    borderColor: "rgba(0, 255, 255, 0.8)",
                    backgroundColor: "rgba(0, 255, 255, 0.2)"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { type: "time", time: { unit: "minute" } },
                    y: { ticks: { font: { size: 12 } } }
                }
            }
        };

        if (window.priceChart) {
            window.priceChart.destroy();
        }
        window.priceChart = new Chart(ctx, config);
    }

    async function fetchMarketData(symbol) {
        try {
            console.log(`Fetching Market Data for: ${symbol}`);
            const response = await fetch(`http://127.0.0.1:10000/market-data?symbol=${symbol}`);
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
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

            vwapElement.innerHTML = `<b>VWAP:</b> ${data.order_flow.vwap.toFixed(2)}`;
            rsiElement.innerHTML = `<b>RSI:</b> ${data.rsi ? data.rsi.toFixed(2) : "Unavailable"}`;
            supportElement.innerHTML = `<b>Support Levels:</b><br> ${data.support_level.map(s => `S: ${s}`).join("<br>")}`;
            resistanceElement.innerHTML = `<b>Resistance Levels:</b><br> ${data.resistance_level.map(r => `R: ${r}`).join("<br>")}`;

            updatePriceChart(data);
        } catch (error) {
            console.error("Error fetching market data:", error);
            orderFlowElement.innerHTML = "<b>Error fetching order flow.</b>";
            rsiElement.innerHTML = "<b>Error fetching RSI.</b>";
        }
    }

    function triggerDataFetch() {
        const symbol = symbolInput.value.trim().toUpperCase();
        if (!symbol) {
            console.log("No symbol entered. Data fetch skipped.");
            return;
        }
        console.log(`Fetching Data for Symbol: ${symbol}`);
        fetchMarketData(symbol);
    }

    fetchDataBtn.addEventListener("click", triggerDataFetch);
    symbolInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            triggerDataFetch();
        }
    });
});
