from breeze_connect import BreezeConnect  # Importing the BreezeConnect library to interact with the Breeze API
import pandas as pd  # Importing pandas for data manipulation and analysis
import login as l  # Importing custom login module that contains API credentials


def initializeSymbolTokenMap():
    """
    Function to initialize and update the symbol-token mapping.
    This function fetches the latest stock symbols and their corresponding tokens from a CSV file
    and stores it in a global variable for later use.
    """
    # Load the stock symbol data from a CSV file available online, updated daily at 8:00 AM
    tokendf = pd.read_csv('https://traderweb.icicidirect.com/Content/File/txtFile/ScripFile/StockScriptNew.csv')
    l.tokendf = tokendf  # Store the loaded data in the login module for access later
    print(tokendf)  # Print the DataFrame to the console for verification


def getTokenInfo(instrumentName, exchange, instrumentType, Segment="", strike=0, optionType='', expiry=''):
    """
    Function to retrieve token information for a specific instrument based on its name, exchange, and type.

    Parameters:
    - instrumentName: Name of the stock or derivative.
    - exchange: The exchange where the instrument is listed (e.g., NSE, NFO).
    - instrumentType: Type of instrument (e.g., EQUITY or DERIVATIVE).
    - Segment, strike, optionType, expiry: Optional parameters for derivatives (not used for EQUITY).

    Returns:
    - A DataFrame row containing the token information for the specified instrument.
    """

    # Retrieve information for Cash Stock (EQUITY)
    if instrumentType == 'EQUITY':
        df = l.tokendf  # Access the global token DataFrame
        eq_df = df[(df.EC == exchange) & (df.NS == instrumentName) & (df.SG == instrumentType)]
        return eq_df.iloc[0]  # Return the first matching row as a Series

    # Retrieve information for Stock Future (DERIVATIVE)
    if instrumentType == 'DERIVATIVE':
        df = l.tokendf  # Access the global token DataFrame
        stockfuture = df[(df.EC == exchange) & (df.NS == instrumentName) & (df.SG == instrumentType)]
        return stockfuture.iloc[0]  # Return the first matching row as a Series


# Create a BreezeConnect instance using the API key from the login module
breeze = BreezeConnect(api_key=l.api_key)

# Print the login URL for API user login, encoding the API key for safe URL formatting
import urllib

print("https://api.icicidirect.com/apiuser/login?api_key=" + urllib.parse.quote_plus(l.api_key))

# Generate a session using the API secret and session token from the login module
print(breeze.generate_session(api_secret=l.api_secret, session_token=l.session_key))

# Initialize the symbol-token map by fetching the latest data
initializeSymbolTokenMap()

# Get unique stock names from the NSE (National Stock Exchange)
ls = l.tokendf[l.tokendf.EC == "NSE"].NS.unique()
print(ls[0:100])  # Print the first 100 unique stock names

# Get unique stock names for a specific instrument (IDEA) from the token DataFrame
ls = l.tokendf[l.tokendf.NS == "IDEA"].NS.unique()
print(ls[0:30])  # Print the first 30 unique names for IDEA

# Retrieve and print the token information for the stock "IDEA" as an EQUITY (Cash Stock)
print("Stock Cash Token")
token = getTokenInfo("IDEA", "NSE", "EQUITY")
print(token['SC'])  # Print the stock code for verification

# Retrieve and print the token information for the stock "IDEA" as a DERIVATIVE (Stock Future)
print("Stock Future Token")
token = getTokenInfo("IDEA", "NFO", "DERIVATIVE")
print(token['SC'])  # Print the stock code for verification

# Retrieve and print the token information for the stock "IDEA" as a DERIVATIVE (Stock Option)
print("Stock Option Token")
token = getTokenInfo("IDEA", "NFO", "DERIVATIVE")
print(token['SC'])  # Print the stock code for verification

"""
# Uncomment the following lines to get the token information for the NIFTY BANK index in the cash market
print("Index Spot")
token = getTokenInfo("NIFTY BANK", "NSE", "EQUITY")
print(token['SC'])
"""

# Retrieve and print the token information for the NIFTY BANK index as a DERIVATIVE (Index Future)
print("Index Future")
token = getTokenInfo("NIFTY BANK", "NFO", "DERIVATIVE")
print(token['TK'])  # Print the token for the index future

# Retrieve and print the token information for the NIFTY BANK index as a DERIVATIVE (Index Option)
print("Index Option Token")
token = getTokenInfo("NIFTY BANK", "NFO", "DERIVATIVE")
print(token['SC'])  # Print the stock code for verification
