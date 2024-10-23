from breeze_connect import BreezeConnect
import pandas as pd
import login as l
import hashlib
import hmac
import base64
import time
import datetime

# Initialize the symbol token map by downloading the CSV file
# This file contains the necessary tokens for all instruments (stocks, futures, options, etc.)
def initializeSymbolTokenMap():
    # Every day at 8:00 AM the file is updated, so make sure to refresh daily
    tokendf = pd.read_csv('https://traderweb.icicidirect.com/Content/File/txtFile/ScripFile/StockScriptNew.csv')
    l.tokendf = tokendf  # Store the DataFrame globally in the login module (l)
    print(tokendf)  # Print to verify that data is correctly loaded


# Get token information for specific instruments based on type (equity, derivative, etc.)
# Supports both stocks and futures
def getTokenInfo(instrumentName, exchange, instrumentType, Segment="", strike=0, optionType='', expiry=''):
    # For cash stock (equity)
    if instrumentType == 'EQUITY':
        df = l.tokendf  # Fetch token DataFrame from login module
        # Filter DataFrame for the required stock in the specified exchange and instrument type
        eq_df = df[(df.EC == exchange) & (df.NS == instrumentName) & (df.SG == instrumentType)]
        if not eq_df.empty:
            return eq_df.iloc[0]  # Return the first matching row (token info)
        else:
            print(f"Token not found for {instrumentName} in {exchange}")
            return None

    # For stock future (derivative)
    if instrumentType == 'DERIVATIVE':
        df = l.tokendf  # Fetch token DataFrame from login module
        # Filter DataFrame for the required stock future in the specified exchange and instrument type
        stockfuture = df[(df.EC == exchange) & (df.NS == instrumentName) & (df.SG == instrumentType)]
        if not stockfuture.empty:
            return stockfuture.iloc[0]  # Return the first matching row (token info)
        else:
            print(f"Token not found for {instrumentName} in {exchange}")
            return None


# Initialize the BreezeConnect API with API key
breeze = BreezeConnect(api_key=l.api_key)

# Print login URL for generating session token
import urllib
print("https://api.icicidirect.com/apiuser/login?api_key=" + urllib.parse.quote_plus(l.api_key))

# Generate session using API secret and session token
print(breeze.generate_session(api_secret=l.api_secret, session_token=l.session_key))

# Initialize token map (download the CSV file containing token information)
initializeSymbolTokenMap()

# Get available funds using Breeze API
print(breeze.get_funds())

# Example of fetching and saving historical data for Nifty Bank futures
print("Index Futures")

# Retrieve token information for "NIFTY BANK" in NFO (National Futures & Options market)
token = getTokenInfo("NIFTY BANK", "NFO", "DERIVATIVE")
if token:
    print(token['SC'])  # Print the token code for Nifty Bank futures

    # Fetch historical data for the specified instrument and time range
    res = breeze.get_historical_data(
        interval="5minute",  # 5-minute intervals
        from_date="2024-03-01T07:00:00.000Z",  # Start date of historical data
        to_date="2024-03-28T07:00:00.000Z",  # End date of historical data
        stock_code=token['SC'],  # Stock token code
        exchange_code="NFO",  # Exchange (NFO for futures)
        product_type="",  # Product type (not specified here)
        expiry_date="2024-03-28T07:00:00.000Z",  # Expiry date of futures contract
        option_type="others",  # Option type (here it's futures, so "others")
        strike_price=""  # No strike price for futures
    )

    # Check if the request was successful
    if 'Success' in res:
        # Convert the response data into a DataFrame
        df = pd.DataFrame(res['Success'])
        # Save the DataFrame to a CSV file for future reference
        df.to_csv("indexfuturesdata.csv", index=False)
        # Print the DataFrame for verification
        print(df)
    else:
        print(f"Failed to fetch historical data for {token['SC']}")
else:
    print("Token information for NIFTY BANK futures could not be found.")
