import pandas as pd
from breeze_connect import BreezeConnect


# Setting up API keys and session tokens for the BreezeConnect API
# These credentials are necessary to authenticate your connection and access data.
app_key = '18EBn*393750~DA17w916OF4n4dz742L'
secret_key = '9979M8~98IGru2T742889PL9F2883044'
session_token = "48439132"


# Initialize the BreezeConnect API client with your API key.
api = BreezeConnect(api_key=app_key)

# Generate a session by providing the secret key and session token.
# This step is required to authenticate your session and make API requests.
api.generate_session(api_secret=secret_key, session_token=session_token)

try:
    # Fetch historical options data for Bank Nifty with a 5-minute interval.
    # from_date and to_date define the time range, stock_code is for Bank Nifty (CNXBAN),
    # and product_type is set to 'options' with a specified strike price and expiry date.
    data_call = api.get_historical_data(interval="5minute",
                                        from_date="2024-02-01T07:00:00.000Z",
                                        to_date="2024-03-07T07:00:00.000Z",
                                        stock_code="CNXBAN",
                                        exchange_code="NFO",
                                        product_type="options",
                                        expiry_date="2024-03-06T07:00:00.000Z",
                                        strike_price="46200")

    # Convert the retrieved data into a pandas DataFrame for easier manipulation.
    call_data = pd.DataFrame(data_call['Success'])
    print(call_data)  # Display the fetched call option data.

    # Save the call option data to a CSV file for later analysis.
    call_data.to_csv('call_data.csv')

# Handle any exceptions that occur during the API request (e.g., connectivity issues, incorrect API parameters).
except Exception as e:
    print("In Exception")
    print("An error occurred:", e)

# Fetch historical options data for Bank Nifty put options with a 1-minute interval.
# The parameters are similar to the previous call but for a shorter time frame and different interval.
data_put = api.get_historical_data(interval="1minute",
                                   from_date="2024-03-01T07:00:00.000Z",
                                   to_date="2024-03-01T07:00:00.000Z",
                                   stock_code="CNXBAN",
                                   exchange_code="NFO",
                                   product_type="options",
                                   expiry_date="2024-03-06T07:00:00.000Z",
                                   strike_price="46200")

# Convert the retrieved put options data into a pandas DataFrame.
put_data = pd.DataFrame(data_put['Success'])

# Save the put option data to a CSV file.
put_data.to_csv('put_data.csv')

"""
# Uncommented section below for fetching Bank Nifty data without options:
# Fetch historical data for Bank Nifty index itself, not options.
Banknifty = api.get_historical_data(interval="5minute",
                                    from_date="2024-02-01T07:00:00.000Z",
                                    to_date="2024-03-08T07:00:00.000Z",
                                    stock_code="CNXBAN",
                                    exchange_code="NSE")

# Convert to pandas DataFrame and store.
Banknifty_data = pd.DataFrame(Banknifty['Success'])
"""
