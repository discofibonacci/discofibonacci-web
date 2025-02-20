document.addEventListener("DOMContentLoaded", function () {
    const fetchData = async () => {
        const symbol = document.getElementById("symbolInput").value.toUpperCase() || "AAPL";

        // Show loading message
        document.getElementById("orderFlow").innerHTML = "<i>Loading...</i>";
        document.getElementById("supportLevel").textContent = "Loading...";
        document.getElementById("rsi").textContent = "Loading...";

        try {
            const response = await fetch(`http://127.0.0.1:10000/market-data?symbol=${symbol}`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();

            // Format order flow data
            document.getElementById("orderFlow").innerHTML = data.order_flow
    ? `<b>Open:</b> ${data.order_flow.open.toFixed(2)}<br>
       <b>High:</b> ${data.order_flow.high.toFixed(2)}<br>
       <b>Low:</b> ${data.order_flow.low.toFixed(2)}<br>
       <b>Close:</b> ${data.order_flow.close.toFixed(2)}<br>
       <b>Volume:</b> ${data.order_flow.volume.toLocaleString()}`
    : "No valid order flow data found.";


            // **Fix: Ensure Support & Resistance Display Properly**
            document.getElementById("supportLevel").innerHTML = 
    `🔵 <b>Support Levels:</b><br> 
     S1: ${parseFloat(data.support_level.split(", ")[0]).toFixed(2)}<br> 
     S2: ${parseFloat(data.support_level.split(", ")[1]).toFixed(2)}<br><br>
     🔴 <b>Resistance Levels:</b><br> 
     R1: ${parseFloat(data.resistance_level.split(", ")[0]).toFixed(2)}<br> 
     R2: ${parseFloat(data.resistance_level.split(", ")[1]).toFixed(2)}`;

            // Display RSI with proper formatting
            document.getElementById("rsi").textContent = 
                (typeof data.rsi === "number" && !isNaN(data.rsi)) 
                    ? `RSI: ${data.rsi.toFixed(2)}` 
                    : "RSI data unavailable.";

        } catch (error) {
            document.getElementById("orderFlow").textContent = "Error fetching order flow.";
            document.getElementById("supportLevel").textContent = "Error fetching support/resistance levels.";
            document.getElementById("rsi").textContent = "Error fetching RSI.";
            console.error("Error fetching market data:", error);
        }
    };

    // Fetch data when clicking the button
    document.getElementById("fetchData").addEventListener("click", fetchData);

    // Fetch data when pressing Enter in the input field
    document.getElementById("symbolInput").addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            fetchData();
        }
    });
});
