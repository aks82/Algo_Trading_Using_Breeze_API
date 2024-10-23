from breeze_connect import BreezeConnect
import pandas as pd
import login as l  # Importing a custom module 'login' which handles the login credentials
import hashlib
import hmac
import base64
import time
import datetime


def initializeSymbolTokenMap():
    """
    This function retrieves and updates the stock symbol-token mapping.
    It reads a CSV file containing stock script data and stores it in a DataFrame.
    This is done every day at 8:00 AM.
    """
    tokendf = pd.read_csv('https://traderweb.icicidirect.com/Content/File/txtFile/ScripFile/StockScriptNew.csv')
    l.tokendf = tokendf  # Storing the DataFrame in the login module's variable
    print(tokendf)


def getTokenInfo(instrumentName, exchange, instrumentType, Segment="", strike=0, optionType='', expiry=''):
    """
    This function fetches the token information for a given instrument (stock or derivative).
    It looks up the token in the DataFrame based on the provided instrument name, exchange, and type.
    """

    # For cash stocks (equity)
    if instrumentType == 'EQUITY':
        df = l.tokendf
        # Filter the DataFrame to match the stock by name, exchange, and segment (e.g., equity)
        eq_df = df[(df.EC == exchange) & (df.NS == instrumentName) & (df.SG == instrumentType)]
        return eq_df.iloc[0]  # Return the first matching result

    # For stock futures (derivatives)
    if instrumentType == 'DERIVATIVE':
        df = l.tokendf
        eq_df = df[(df.EC == exchange) & (df.NS == instrumentName) & (df.SG == instrumentType)]
        return eq_df.iloc[0]  # Return the first matching result


# Initialize the BreezeConnect API using the credentials from the 'login' module
breeze = BreezeConnect(api_key=l.api_key)

# Generate a login URL for the API
import urllib

print("https://api.icicidirect.com/apiuser/login?api_key=" + urllib.parse.quote_plus(l.api_key))

# Generate the session using secret key and session token from the 'login' module
print(breeze.generate_session(api_secret=l.api_secret, session_token=l.session_key))

# Update the symbol-token mapping by calling the initialization function
initializeSymbolTokenMap()

# Fetch and print the token for a stock (IDEA) in the cash segment (EQUITY) on NSE
print("Stock Cash Token")
token = getTokenInfo("IDEA", "NSE", "EQUITY")
print(token['SC'])  # 'SC' is the stock code (token) for the stock

# Fetch historical data for the stock using the retrieved token (5-minute interval data)
res = breeze.get_historical_data(interval="5minute",
                                 from_date="2024-03-01T07:00:00.000Z",
                                 to_date="2024-03-28T07:00:00.000Z",
                                 stock_code=token['SC'],  # Use the stock token from the previous step
                                 exchange_code="NFO",  # NFO stands for the National Futures and Options segment
                                 product_type="",
                                 expiry_date="",
                                 strike_price=""
                                 )

# Convert the retrieved historical data into a DataFrame and save it to a CSV file
data_items = res['Success']
print(data_items)  # Print the fetched data
dlist = list(data_items)
df = pd.DataFrame(dlist)  # Convert the list of data to a pandas DataFrame
print(df)
df.to_csv("cashdata.csv")  # Save the DataFrame to 'cashdata.csv' file

# Fetch and print the token for a stock future (IDEA) in the derivative segment (NFO)
print("Stock Future Token")
token = getTokenInfo("IDEA", "NFO", "DERIVATIVE")
print(token)  # Print the retrieved token
