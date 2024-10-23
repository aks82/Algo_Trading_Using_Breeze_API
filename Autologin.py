# Importing necessary libraries and modules
from breeze_connect import BreezeConnect  # For API access to BreezeConnect for stock data and trading
from tabulate import tabulate  # To format data in tabular form
from selenium import webdriver  # For automating browser tasks (used in auto-login)
from pyotp import TOTP  # For generating Time-Based One-Time Passwords (2FA)
import urllib  # URL handling module
import pandas as pd  # To handle and manipulate data in a tabular format
import login as l  # Importing custom login module (contains user credentials and API tokens)
import numpy as np  # For numerical operations and handling arrays
from datetime import datetime  # For handling date and time operations
from time import time, sleep  # For time-based operations like delays
import sys  # System-specific parameters and functions
import threading  # To handle concurrent execution (multithreading)
import warnings  # To handle warnings
import time  # Time module for delays
import os  # For operating system interactions (file paths, environment variables, etc.)


# Function for automatically logging into the trading platform using Selenium
def autologin():
    # Launch the Chrome browser using Selenium WebDriver
    browser = webdriver.Chrome()

    # Navigate to the login page with the API key
    browser.get("https://api.icicidirect.com/apiuser/login?api_key=" + urllib.parse.quote_plus(l.api_key))

    # Implicit wait to ensure page elements are loaded
    browser.implicitly_wait(10)

    # Initialize the BreezeConnect API client with the provided API key
    breeze = BreezeConnect(api_key=l.api_key)

    # Find username and password input fields on the login page using XPaths
    username = browser.find_element("xpath", '/html/body/form/div[2]/div/div/div[1]/div[2]/div/div[1]/input')
    password = browser.find_element("xpath", '/html/body/form/div[2]/div/div/div[1]/div[2]/div/div[3]/div/input')

    # Input the user credentials from the 'login' module
    username.send_keys(l.userID)
    username.send_keys(l.password)

    # Check the checkbox for agreeing to terms (or similar)
    browser.find_element("xpath", '/html/body/form/div[2]/div/div/div[1]/div[2]/div/div[4]/div/input').click()

    # Click the login button
    browser.find_element("xpath", '/html/body/form/div[2]/div/div/div[1]/div[2]/div/div[5]/input[1]').click()

    # Delay to allow the page to process the login
    time.sleep(2)

    # Find the PIN input field and generate a Time-Based One-Time Password (TOTP) for 2FA
    pin = browser.find_element("xpath",
                               '/html/body/form/div[2]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div[1]/input').click()

    # Generate the current TOTP using the 'login' module's secret
    topt = TOTP(l.totp)
    token = topt.now()

    # Enter the generated token into the PIN field
    pin.send_keys(token)

    # Confirm the login by clicking the submit button
    browser.find_element("xpath",
                         '/html/body/form/div[2]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div[1]/input').click()

    # Delay to allow login process to complete
    time.sleep(1)

    # Extract the temporary session token from the current URL
    temp_token = browser.current_url.split('apisession=')[1][:8]

    # Print the temporary session token (can be saved or logged for further use)
    print('temp_token is: ', temp_token)

    # Generate a session for BreezeConnect using the secret and session token from the 'login' module
    breeze.generate_session(api_secret=l.api_secret, session_token=l.session_key)

    # Print the available funds in the trading account after login
    print(breeze.get_funds())

    # Close the browser once the process is complete
    browser.quit()


# Helper function for logging into the API manually
def login():
    # Initialize BreezeConnect API client using the credentials from the 'login' module
    breeze = BreezeConnect(api_key=l.api_key)

    # Print the login URL to manually generate the session key
    import urllib
    print("https://api.icicidirect.com/apiuser/login?api_key=" + urllib.parse.quote_plus(l.api_key))

    # Generate a session using the secret key and session token from the 'login' module
    breeze.generate_session(api_secret=l.api_secret, session_token=l.session_key)

    # Generate ISO 8601 formatted date/time strings
    import datetime
    iso_date_string = datetime.datetime.strptime("28/02/2021", "%d/%m/%Y").isoformat()[:10] + 'T05:30:00.000Z'
    iso_date_time_string = datetime.datetime.strptime("28/02/2021 23:59:59", "%d/%m/%Y %H:%M:%S").isoformat()[
                           :19] + '.000Z'

    # Re-generate session (optional, in case it's needed)
    breeze.generate_session(api_secret=l.api_secret, session_token=l.session_key)

    # Print the available funds to confirm successful login
    print(breeze.get_funds())


# Call the login function to initiate the process
login()
