import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import requests

def fetch_crypto_data(coin_id='bitcoin', vs_currency='usd', days=30):
    """
    Fetch cryptocurrency data from CoinGecko API.

    :param coin_id: ID of the cryptocurrency (e.g., 'bitcoin', 'ethereum')
    :param vs_currency: The target currency of market data (usd, eur, jpy, etc.)
    :param days: Number of days of data to retrieve
    :return: DataFrame with 'timestamp' and 'close' columns
    """
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        'vs_currency': vs_currency,
        'days': days
    }

    response = requests.get(url, params=params)
    data = response.json()

    df = pd.DataFrame(data['prices'], columns=['timestamp', 'close'])
    return df


def analyze_volatility(data, timezone_offset=0):
    """
    Analyze volatility by hour of the day.

    :param data: DataFrame with 'timestamp' and 'close' columns
    :param timezone_offset: Hours to offset for desired timezone (e.g., -4 for ET)
    :return: DataFrame with hourly volatility
    """
    # Convert timestamp to datetime and adjust for timezone
    data['datetime'] = pd.to_datetime(data['timestamp'], unit='ms')
    data['datetime'] = data['datetime'] + timedelta(hours=timezone_offset)

    # Calculate returns
    data['returns'] = data['close'].pct_change()

    # Group by hour and calculate volatility
    hourly_volatility = data.groupby(data['datetime'].dt.hour)['returns'].agg(['std', 'count'])
    hourly_volatility.columns = ['volatility', 'sample_size']
    hourly_volatility = hourly_volatility.sort_index()

    return hourly_volatility


# Fetch data and analyze
#coin_id = 'ethereum'  # You can change this to any coin ID supported by CoinGecko
coin_id = 'bitcoin'
#coin_id = 'ripple'
days = 2  # Adjust as needed
timezone_offset = 5.5  # For India Time

df = fetch_crypto_data(coin_id, days=days)
result = analyze_volatility(df, timezone_offset=timezone_offset)

print(f"Hourly volatility for {coin_id} over the last {days} days:")
print(result)



