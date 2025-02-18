import yahoo_fin.stock_info as si
import pandas as pd
import requests
from io import StringIO

# Fix Yahoo Finance's broken get_quote_table function
def patched_get_quote_table(ticker, dict_result=True):
    """Fetch stock summary from Yahoo Finance with updated structure."""
    url = f"https://finance.yahoo.com/quote/{ticker}?p={ticker}&.tsrc=fin-srch"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    tables = pd.read_html(StringIO(response.text), flavor="bs4")  # Fix read_html issue

    if len(tables) > 1:
        data = pd.concat([tables[0], tables[1]], ignore_index=True)  # Fix append() issue
    else:
        data = tables[0]

    if dict_result:
        return dict(zip(data.iloc[:, 0], data.iloc[:, 1]))  # Return proper key-value pairs
    return data

# Override the broken function in yahoo_fin
si.get_quote_table = patched_get_quote_table
