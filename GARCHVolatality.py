import pandas as pd
import numpy as np
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from arch import arch_model

def calculate_garch_volatility(returns):
    # Rescale y by a factor of 100
    y_rescaled = 1000 * returns
    model = arch_model(y_rescaled, vol='GARCH', p=1, q=1)
    results = model.fit(disp='off')
    return results.conditional_volatility


def detect_volatility_spike(volatility_series, window=5, threshold=2):
    # Calculate the rolling mean and standard deviation
    rolling_mean = volatility_series.rolling(window=window).mean()
    rolling_std = volatility_series.rolling(window=window).std()

    # Calculate z-scores
    z_scores = (volatility_series - rolling_mean) / rolling_std

    # Detect spikes
    spikes = z_scores > threshold

    # Calculate the magnitude of the most recent spike
    if spikes.iloc[-window:].any():
        recent_spike = z_scores.iloc[-window:][spikes.iloc[-window:]].max()
    else:
        recent_spike = 0

    return recent_spike

def fetch_crypto_data(coin_id, symbol, days=7, max_retries=3):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {'vs_currency': 'usd', 'days': days}

    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if 'prices' not in data or not data['prices'] or 'total_volumes' not in data or not data[
                    'total_volumes']:
                    raise Exception("No price or volume data available")
                df = pd.DataFrame({
                    'timestamp': [p[0] for p in data['prices']],
                    'price': [p[1] for p in data['prices']],
                    'volume': [v[1] for v in data['total_volumes']]
                })
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                return df
            elif response.status_code == 404:
                # Try with symbol if coin_id fails
                url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart"
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    # Process successful response (same as above)
                    data = response.json()
                    if 'prices' not in data or not data['prices'] or 'total_volumes' not in data or not data[
                        'total_volumes']:
                        raise Exception("No price or volume data available")
                    df = pd.DataFrame({
                        'timestamp': [p[0] for p in data['prices']],
                        'price': [p[1] for p in data['prices']],
                        'volume': [v[1] for v in data['total_volumes']]
                    })
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df.set_index('timestamp', inplace=True)
                    return df
                else:
                    print(f"Data not found for both {coin_id} and {symbol}")
                    return None
            elif response.status_code == 429:
                wait_time = 60 * (2 ** attempt)  # Exponential backoff
                print(f"Rate limit hit for {coin_id}, waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                print(f"Unexpected status code {response.status_code} for {coin_id}")
                return None
        except Exception as e:
            print(f"Request failed for {coin_id}: {str(e)}")
            time.sleep(5)  # Wait a bit before retrying

        print(f"Failed to fetch data for {coin_id} after {max_retries} attempts")
        return None

def calculate_range_bound_score(df):
    returns = df['price'].pct_change().dropna()

    # Calculate GARCH volatility
    garch_vol = calculate_garch_volatility(returns)

    # Detect volatility spikes
    volatility_spike = detect_volatility_spike(garch_vol)

    # Use the average GARCH volatility as a measure of overall volatility
    avg_garch_vol = garch_vol.mean()

    price_range = df['price'].max() - df['price'].min()
    avg_price = df['price'].mean()
    normalized_range = price_range / avg_price

    volume_volatility = df['volume'].pct_change().std()

    # Incorporate GARCH volatility into the score
    range_bound_score = 1 / (normalized_range * avg_garch_vol * volume_volatility)

    return range_bound_score, volatility_spike

def analyze_crypto(coin_id, symbol):
    try:
        df = fetch_crypto_data(coin_id, symbol)
        if df is None or len(df) < 2:
            return coin_id, symbol, None, None, None, "Insufficient data points"

        score, volatility_spike = calculate_range_bound_score(df)
        avg_volume = df['volume'].mean()

        return coin_id, symbol, score, avg_volume, volatility_spike, None
    except Exception as e:
        return coin_id, symbol, None, None, None, str(e)


def get_top_coins(limit=100):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {'vs_currency': 'usd', 'order': 'market_cap_desc', 'per_page': limit, 'page': 1}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch top coins. Status code: {response.status_code}")
    data = response.json()
    return [(coin['id'], coin['symbol'].lower()) for coin in data]  # Return both id and symbol

def get_binance_futures_symbols():
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch Binance futures info. Status code: {response.status_code}")
    data = response.json()
    return [symbol['baseAsset'].lower() for symbol in data['symbols'] if symbol['contractType'] == 'PERPETUAL']


def main():
    print("Fetching top coins...")
    top_coins = get_top_coins(limit=100)
    print(f"Fetched {len(top_coins)} top coins")

    print("Fetching Binance futures symbols...")
    binance_futures = get_binance_futures_symbols()
    print(f"Fetched {len(binance_futures)} Binance futures symbols")

    futures_coins = [(coin_id, symbol) for coin_id, symbol in top_coins if symbol in binance_futures]
    print(f"Found {len(futures_coins)} coins available in Binance futures")
    results = []
    errors = []

    print("Analyzing coins...")
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_coin = {executor.submit(analyze_crypto, coin, symbol): (coin, symbol) for coin, symbol in
                          futures_coins}
        for future in as_completed(future_to_coin):
            coin_id, symbol = future_to_coin[future]
            try:
                result = future.result()
                if result[2] is not None:  # If score is not None
                    results.append(result)
                    print(f"Successfully analyzed {result[0]} ({result[1]})")
                else:
                    errors.append((result[0], result[1], result[4]))  # coin_id, symbol, error message
                    print(f"Failed to analyze {result[0]} ({result[1]}): {result[4]}")
            except Exception as e:
                errors.append((coin_id, symbol, str(e)))
                print(f"Error processing {coin_id} ({symbol}): {str(e)}")
            time.sleep(1)  # Delay between requests

    results.sort(key=lambda x: (x[2] or 0, x[3] or 0), reverse=True)  # Sort by score, then by avg_volume

    print("\nTop 15 Most Range-Bound Cryptocurrencies (Available in Binance Futures) in the Last 7 Days:")
    for i, (coin_id, symbol, score, avg_volume, volatility_spike, _) in enumerate(results[:15], 1):
        if score is not None and avg_volume is not None and volatility_spike is not None:
            print(f"{i}. {coin_id} ({symbol}): Score = {score:.4f}, Avg Daily Volume = ${avg_volume / 1:,.2f},Volatility Spike = {volatility_spike:.4f}")
        else:
            print(f"{i}. {coin_id} ({symbol}): Data unavailable")

    if errors:
        print("\nCoins that couldn't be analyzed:")
        for coin_id, symbol, error in errors:
            print(f"{coin_id} ({symbol}): {error}")

if __name__ == "__main__":
    main()