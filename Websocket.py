from breeze_connect import BreezeConnect  # Importing the BreezeConnect library to interact with the Breeze API
from tabulate import tabulate  # Importing tabulate for pretty printing DataFrames
import pandas as pd  # Importing pandas for data manipulation and analysis
import login as l  # Importing custom login module that contains API credentials
import numpy as np  # Importing NumPy for numerical operations (not currently used)
from datetime import datetime  # Importing datetime for handling date and time
from time import time, sleep  # Importing time functions for delays and timestamps
import sys  # Importing sys for system-specific parameters and functions
import threading  # Importing threading for creating and managing threads (not currently used)
import warnings  # Importing warnings to manage warning messages (not currently used)


def initializeSymbolTokenMap():
    """
    Function to initialize and update the symbol-token mapping.
    Fetches the latest stock symbols and their corresponding tokens from a CSV file
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
    - Segment, strike, optionType, expiry: Optional parameters for derivatives (not used here).

    Returns:
    - A Series containing the token information for the specified instrument.
    """

    # Retrieve information for Cash Stock (EQUITY)
    if instrumentType == 'EQUITY':
        df = l.tokendf  # Access the global token DataFrame
        eq_df = df[(df.EC == exchange) & (df.NS == instrumentName) & (df.SG == instrumentType)]
        return eq_df.iloc[0] if not eq_df.empty else None  # Return the first matching row if not empty

    # Retrieve information for Stock Future (DERIVATIVE)
    if instrumentType == 'DERIVATIVE':
        df = l.tokendf  # Access the global token DataFrame
        stockfuture = df[(df.EC == exchange) & (df.NS == instrumentName) & (df.SG == instrumentType)]
        return stockfuture.iloc[0] if not stockfuture.empty else None  # Return the first matching row if not empty


if __name__ == '__main__':
    # Create a BreezeConnect instance using the API key from the login module
    breeze = BreezeConnect(api_key=l.api_key)

    # Generate a session using the API secret and session token from the login module
    print(breeze.generate_session(api_secret=l.api_secret, session_token=l.session_key))

    # Initialize the symbol-token map by fetching the latest data
    initializeSymbolTokenMap()

    # Retrieve and print the token information for the stock "IDEA" as an EQUITY (Cash Stock)
    token = getTokenInfo("IDEA", "NSE", "EQUITY")
    if token is not None:
        print(token['TK'])  # Print the token if found

    # Connect to the WebSocket for real-time data
    breeze.ws_connect()


    # Define a callback function to handle incoming ticks (real-time market data)
    def on_ticks(ticks):
        print("Ticks: {}".format(ticks))  # Print the received ticks to the console


    breeze.on_ticks = on_ticks  # Assign the callback function to the BreezeConnect instance

    # Print the token of the subscribed stock
    print("Token is: " + str(token['TK']))

    # Uncomment the following line to subscribe to stock feeds by stock-token
    # breeze.subscribe_feeds(stock_token="4.1!{0}".format(str(token['TK'])))

    # Uncommenting these lines allows you to subscribe to market data for specific stocks or options
    # For options
    # breeze.subscribe_feeds(exchange_code="NFO", stock_code="YESBAN", product_type="options", expiry_date="28-Mar-2024", strike_price="25", right="Call", get_exchange_quotes=True, get_market_depth=False)

    # For futures subscription
    breeze.ws_disconnect()  # Disconnecting WebSocket before subscribing to futures
    breeze.subscribe_feeds(exchange_code="NFO", stock_code="INFTEC", product_type="futures", expiry_date="28-Mar-2024",
                           strike_price="", right="others", get_exchange_quotes=True, get_market_depth=False)

    # Uncomment these lines to subscribe to specific stock tokens
    # breeze.subscribe_feeds(stock_token="1.1!532822")
    # breeze.subscribe_feeds(stock_token="4.1!14366")

    # Main loop to keep the program running until a specific time
    while True:
        now = datetime.now()  # Get the current date and time
        # Exit the program if the current time is 3:30 PM or later
        if (now.hour >= 15 and now.minute >= 30):
            sys.exit()  # Terminate the program
        sleep(5)  # Wait for 5 seconds before the next iteration
        print("New Iteration")  # Indicate a new iteration of the loop
