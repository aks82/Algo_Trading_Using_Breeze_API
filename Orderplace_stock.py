from breeze_connect import BreezeConnect  # Import the BreezeConnect API module
import pandas as pd  # For data manipulation
import login as l  # Custom module for storing credentials and token info


# Function to initialize the token map by downloading the stock script file
# This file contains all the stock/futures options with their respective tokens
def initializeSymbolTokenMap():
    # Every day at 8:00 AM the file is updated on the server
    tokendf = pd.read_csv('https://traderweb.icicidirect.com/Content/File/txtFile/ScripFile/StockScriptNew.csv')
    l.tokendf = tokendf  # Save the DataFrame to the login module for later use
    print(tokendf)  # Print the token data for verification


# Function to retrieve token information based on instrument type (equity or derivative)
def getTokenInfo(instrumentName, exchange, instrumentType, Segment="", strike=0, optionType='', expiry=''):
    # For cash stock (equity), filter the DataFrame to find the token for the specified stock and exchange
    if instrumentType == 'EQUITY':
        df = l.tokendf  # Fetch token DataFrame
        eq_df = df[(df.EC == exchange) & (df.NS == instrumentName) & (df.SG == instrumentType)]
        return eq_df.iloc[0]  # Return the first matching row (token info)

    # For stock futures, filter the DataFrame to find the token for the specified futures contract
    if instrumentType == 'DERIVATIVE':
        df = l.tokendf  # Fetch token DataFrame
        stockfuture = df[(df.EC == exchange) & (df.NS == instrumentName) & (df.SG == instrumentType)]
        return stockfuture.iloc[0]  # Return the first matching row (token info)


# Initialize BreezeConnect with API key
breeze = BreezeConnect(api_key=l.api_key)

# Print login URL for generating session token
import urllib

print("https://api.icicidirect.com/apiuser/login?api_key=" + urllib.parse.quote_plus(l.api_key))

# Generate session with API secret and session token (needed to interact with the API)
print(breeze.generate_session(api_secret=l.api_secret, session_token=l.session_key))

# Initialize the symbol token map (download the CSV file containing all stock/future tokens)
initializeSymbolTokenMap()

# Fetch and print available funds in the trading account
print("\n\n\n*********\n\n\n")
print(breeze.get_funds())

# Example of placing an order for an equity stock
print("\nStock Equity Order\n")
# Fetch the token for IDEA stock from NSE exchange
token = getTokenInfo("IDEA", "NSE", "EQUITY")

# Print current funds
print("\n\n\n*****Current funds...*****")
print(breeze.get_funds())

# Debit some amount from the account to simulate a fund reduction
print("\n\n\n*****Reducing funds...*****")
breeze.set_funds(transaction_type="debit", amount="280", segment="Equity")
# Print updated funds after the debit
print(breeze.get_funds())

# The following section is commented out but demonstrates placing an order for a stock
"""
print("\n\n\n ****** Placing order now...*******")

orderid = breeze.place_order(stock_code=token['SC'],
                                   exchange_code="NSE",
                                   product="cash",
                                   action="buy",
                                   order_type="limit",
                                   price="13.85",  # Buying at a limit price of 13.85
                                   stoploss="",
                                   quantity="2",  # Buying 2 shares
                                   validity="day",
                                   user_remark="My Algo Trading"
                                 )
print(orderid)  # Print order ID
print("\n\n\nAvailable funds now are: \n\n\n")
print(breeze.get_funds())  # Print available funds after placing the order
"""

# Example for placing a stock future order (currently commented out)
"""
print("Stock Future Order")
token=getTokenInfo("IDEA", "NFO", "DERIVATIVE")  # Fetch token for stock future
print(token)
orderid = breeze.place_order(stock_code=token['SC'],
                                   exchange_code="NFO",
                                   product_type="futures",
                                   action="buy",
                                   order_type="market",  # Buying at market price
                                   stop_loss="13",
                                   quantity=str(token['LS']),  # Order quantity
                                   price=0,
                                   validity="day",
                                   validity_date="2024-03-12T07:00:00.000Z",  # Validity of the order
                                   disclosed_quantity="0",
                                   expiry_date="2024-03-28T07:00:00.000Z",  # Expiry date of the future contract
                                   right="others",
                                   strike_price="0",
                                   user_remark="Kaustubh's Algo Trading"
                                 )
print(orderid)  # Print order ID
"""

# Example for placing a stock option order (currently commented out)
"""
print("Stock Option Order")
token=getTokenInfo("IDEA", "NFO", "DERIVATIVE")  # Fetch token for stock option
print(token)
orderid = breeze.place_order(stock_code=token['SC'],
                                   exchange_code="NFO",
                                   product_type="options",
                                   action="buy",
                                   order_type="limit",  # Placing a limit order
                                   stop_loss="13",
                                   quantity=str(token['LS']),  # Order quantity
                                   price=0,
                                   validity="day",
                                   validity_date="2024-03-12T07:00:00.000Z",
                                   disclosed_quantity="0",
                                   expiry_date="2024-03-28T07:00:00.000Z",
                                   right="call",  # Option type: Call option
                                   strike_price="14",  # Strike price of the option
                                   user_remark="Kaustubh's Algo Trading"
                                 )
print(orderid)  # Print order ID
"""
