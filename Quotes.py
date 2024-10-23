from breeze_connect import BreezeConnect  # Importing the BreezeConnect library to interact with the Breeze API
from tabulate import tabulate  # Importing tabulate for nicely formatted output tables
import pandas as pd  # Importing pandas for data manipulation and analysis
import login as l  # Importing custom login module that contains API credentials
import numpy as np  # Importing numpy for numerical operations
from datetime import datetime  # Importing datetime for handling date and time
from time import time, sleep  # Importing time functions for delays
import sys  # Importing sys for system-specific parameters and functions
import threading  # Importing threading for concurrent execution
import warnings  # Importing warnings to manage warning messages


def initializeSymbolTokenMap():
    """
    Function to initialize and update the symbol-token mapping.
    This function fetches the latest stock symbols and their corresponding tokens from a CSV file
    and stores it in a global variable for later use.
    """
    # Load the stock symbol data from a CSV file available online, updating it daily at 8:00 AM
    tokendf = pd.read_csv('https://traderweb.icicidirect.com/Content/File/txtFile/ScripFile/StockScriptNew.csv')
    l.tokendf = tokendf  # Store the loaded data in the login module
    print(tokendf)  # Print the DataFrame to the console for verification


def getTokenInfo(instrumentName, exchange, instrumentType, Segment="", strike=0, optionType='', expiry=''):
    """
    Function to retrieve token information for a specific instrument based on its name, exchange, and type.

    Parameters:
    - instrumentName: Name of the stock or derivative.
    - exchange: The exchange where the instrument is listed (e.g., NFO).
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


if __name__ == '__main__':
    # Create a BreezeConnect instance using the API key from the login module
    breeze = BreezeConnect(api_key=l.api_key)
    # Generate a session using the API secret and session token from the login module
    print(breeze.generate_session(api_secret=l.api_secret, session_token=l.session_key))

    # Initialize the symbol-token map by fetching the latest data
    initializeSymbolTokenMap()

    # Get token information for the instrument 'IDEA' listed on NFO as a DERIVATIVE
    token = getTokenInfo("IDEA", "NFO", "DERIVATIVE")
    print(token['SC'])  # Print the stock code for verification

    while True:  # Infinite loop to continuously fetch and display quotes
        print("Option Quote:")
        # Fetch option quotes for the specified instrument
        res = breeze.get_quotes(
            stock_code=token['SC'],
            exchange_code="NFO",
            product_type="options",
            expiry_date="2024-03-28T07:00:00.000Z",  # Specify the expiry date
            right="call",  # Specify the option type
            strike_price="13"  # Specify the strike price
        )
        data_items = res['Success']  # Get the successful response data
        dlist = list(data_items)  # Convert the response to a list
        df = pd.DataFrame(dlist)  # Create a DataFrame from the list

        if not df.empty:  # Check if the DataFrame is not empty
            print(df.iloc[0])  # Print the first row of the DataFrame
        else:
            print("DataFrame is empty")  # Print a message if the DataFrame is empty

        sleep(5)  # Wait for 5 seconds before fetching the future quote

        print("Future Quote:")
        # Fetch future quotes for the specified instrument
        res = breeze.get_quotes(
            stock_code=token['SC'],
            exchange_code="NFO",
            product_type="futures",
            expiry_date="2024-03-28T07:00:00.000Z",  # Specify the expiry date
            right="",  # No option type for futures
            strike_price=""  # No strike price for futures
        )
        data_items1 = res['Success']  # Get the successful response data
        dlist1 = list(data_items1)  # Convert the response to a list
        df1 = pd.DataFrame(dlist1)  # Create a DataFrame from the list

        if not df1.empty:  # Check if the DataFrame is not empty
            print(df1.iloc[0])  # Print the first row of the DataFrame
        else:
            print("DataFrame1 is empty")  # Print a message if the DataFrame is empty
