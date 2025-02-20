import yfinance as yf

symbol = "AAPL"  # Test with Apple stock

try:
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1d", interval="5m")

    if hist.empty:
        print("❌ Yahoo Finance returned empty data.")
    else:
        print("✅ Data received!")
        print(hist.tail())  # Show last few rows

except Exception as e:
    print(f"❌ Error fetching data: {str(e)}")
