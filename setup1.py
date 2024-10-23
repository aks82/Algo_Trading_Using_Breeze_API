from breeze_connect import BreezeConnect
import pandas as pd
import login as l

def initializeSymbolTokenMap():
    tokendf =pd.read_csv('https://traderweb.icicidirect.com/Content/File/txtFile/ScripFile/StockScriptNew.csv')
    print("tokendf")
    print(tokendf)

breeze = BreezeConnect(api_key=l.api_key)

breeze.generate_session(api_secret=l.api_secret, session_token=l.session_key)
#print(1)

#print(breeze.get_funds())

#customer_details = breeze.get_customer_details(l.session_key)
#print(2)
#print(customer_details)

#print(3)
#initializeSymbolTokenMap()

#print(4)
#demat_holdings = breeze.get_demat_holdings()
#print(demat_holdings)

# Get available funds using Breeze API
#print(breeze.get_funds())

# ADD/DEDUCT available funds using Breeze API
#print(breeze.set_funds("Debit","10","Equity"))

#GetHistoricalChartsList
#print(breeze.get_historical_data("1day","2024-10-10","2024-10-22","AXIBAN","NSE"))

#fetch your margin
#print(breeze.get_margin("NSE"))

