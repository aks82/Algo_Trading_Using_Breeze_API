# Import necessary libraries and modules
import login as l  # Custom module containing login credentials and API keys
import json
from datetime import datetime, time  # For handling dates and times
from time import sleep  # For creating delays
import sys  # System-specific parameters and functions
from breeze_connect import BreezeConnect  # Library for connecting to Breeze API

# Define the stock to be traded and other trading parameters
stock = 'ONE97'  # Stock symbol for ONE97 (Paytm)
order_id = ""  # Initialize order ID as empty
price = 500  # Price at which stock will be purchased
cost = 0  # Initialize the cost (buy price) of the stock
trailing_stoploss = 2  # Trailing stop-loss value
qty = 1  # Quantity of stock to be traded
holding_dicts = []  # List to store holdings data

# Define the target time for trading operations to stop
target_time = time(15, 30)  # 3:30 PM
print("\nTarget time is: " + str(target_time) + ".\n")

# Initialize the BreezeConnect API with credentials from the login module
api = BreezeConnect(api_key=l.api_key)
api.generate_session(api_secret=l.api_secret, session_token=l.session_key)

# Function to add funds to the trading account
def add_funds(amt):
    api.set_funds(transaction_type="credit", amount=amt, segment="Equity")
    print("\n************\n")
    print("Updated balance is: ")
    print(api.get_funds())  # Show updated balance
    print("\n************\n")

# Function to buy stock in the cash segment
def buy_stock_in_cash(stock_code, qty):
    global order_id
    # Place a limit order to buy the stock
    buy_order = api.place_order(stock_code=stock_code,
                                exchange_code="NSE",  # NSE Exchange
                                product="cash",  # Product type: cash
                                action='buy',  # Buying action
                                order_type='limit',  # Limit order type
                                stoploss="",  # No stop-loss set here
                                quantity=qty,  # Quantity to buy
                                price=price,  # Buy at the specified price
                                validity="day"  # Valid for the day
                                )
    print("\n*** Printing buy_order ***\n")
    print(buy_order)

    # Check if the order was successful and store the order ID
    if buy_order['Success'] is not None:
        order_id = buy_order['Success']['order_id']
    else:
        print("buy_order['Success'] is None")  # Handle case when the order isn't successful

    print("\n****** Order Placed ******\n")

    # Display order details and trade details for the executed buy order
    print(api.get_order_detail(exchange_code="NSE", order_id=order_id))
    print(api.get_trade_detail(exchange_code="NSE", order_id=order_id))

# Function to get the buy cost (price) of an order
def get_cost(order_id):
    global trailing_stoploss
    global price
    try:
        # Fetch order details and get the average price
        cost = float(api.get_order_detail('NSE', order_id)['Success'][0]['average_price'])
        trailing_stoploss = round((cost - 0.05), 2)  # Update trailing stop-loss based on cost
        price = cost  # Update current price to the buy cost
    except:
        print("\nException while getting the cost price. Cost price set to 0.0\n")
        cost = 0
        trailing_stoploss = cost

    print("\nCost is: " + str(cost))
    return cost

# Function to fetch and print portfolio holdings
def get_my_portfolio_holdings():
    portfolio = api.get_portfolio_holdings("NSE", "", "", stock, "")
    global holding_dicts

    if 'Success' in portfolio:
        holding_list = portfolio['Success']
        if holding_list:
            print("\n*** Portfolio Begins ***\n")
            for holding in holding_list:
                holding_dict = {
                    'stock_code': holding['stock_code'],
                    'quantity': holding['quantity'],
                    'average_price': holding['average_price']
                }
                holding_dicts.append(holding_dict)
        else:
            print("\nPortfolio is empty.\n")
    else:
        print("\nFailed to fetch portfolio holdings.\n")

    for holding_dict in holding_dicts:
        print(holding_dict)
    print("\n*** Portfolio End ***\n")

# Main execution block
if __name__ == '__main__':
    # Connect to the websocket for live price data
    api.ws_connect()

    print(stock + " for qty " + str(qty))

    # Fetch the current price quote for the stock
    quote = api.get_quotes(stock_code=stock, exchange_code="NSE", product_type="cash")
    print(quote)
    price = quote['Success'][0]['ltp']  # Fetch the last traded price (LTP)
    print("\nCurrent price is: " + str(price))

    # Buy the stock
    buy_stock_in_cash(stock, qty)

    print("\n*** Extracting Cost and setting Trailing Stop-loss ***\n")
    cost = float(get_cost(order_id))  # Get the cost of the bought stock
    print("\nCurrent trailing_stoploss is: " + str(trailing_stoploss))

    # Define callback to handle incoming ticks (live price data)
    def on_ticks(ticks):
        global price
        price = ticks.get("last")  # Update the price from live market data

    # Function to monitor the stop-loss and execute sell orders if necessary
    def monitor_stoploss_and_square_off():
        global trailing_stoploss

        # Subscribe to stock feed for live data
        api.subscribe_feeds(exchange_code="NSE", stock_code=stock, product_type="cash",
                            get_exchange_quotes=True, get_market_depth=False)

        api.on_ticks = on_ticks  # Set callback to handle live price updates
        print("\n*** Monitoring live price quotes for stop loss *** \n")

        # Condition 0: Square off if price rises by 5%
        if price > cost * 1.05:
            print("\n*** Squaring off at IF condition 0 *** at price: " + str(price) + ".\n")
            api.place_order(stock_code=stock, exchange_code="NSE", product="cash",
                            action='sell', order_type='market', quantity=qty)

        # Condition 1: Square off if price drops below trailing stop-loss
        if price < trailing_stoploss - 0.05:
            print("\n*** Squaring off at IF condition 1 *** at price: " + str(price) + ".\n")
            api.place_order(stock_code=stock, exchange_code="NSE", product="cash",
                            action='sell', order_type='market', quantity=qty)
            sys.exit(0)

        # Condition 2: Square off if price drops by 5%
        if price < (cost - 0.05):
            print("\n*** Squaring off at IF condition 2 *** at price: " + str(price) + ".\n")
            api.place_order(stock_code=stock, exchange_code="NSE", product="cash",
                            action='sell', order_type='market', quantity=qty)
            sys.exit(0)

        # Adjust the trailing stop-loss if the price increases by a certain amount
        elif price > trailing_stoploss + 0.10:
            trailing_stoploss = round((price - 0.05), 2)
            print("\n*** Revised trailing stoploss to: " + str(trailing_stoploss) + ".\n")

        sleep(2)  # Pause for 2 seconds before the next check

    # Keep monitoring the stop-loss and price until the target time (3:30 PM) is reached
    while datetime.now().time() < target_time:
        monitor_stoploss_and_square_off()
        sleep(2)

    print("\n\n\n*** It's now 3:30 PM. Exiting the trading desk ***\n\n\n")
