import http.client  # For making HTTP requests
import json  # For working with JSON data
from datetime import datetime  # To generate timestamps
import hashlib  # For creating secure hashes (checksum)
import login as l  # Custom module for storing credentials

# App-related keys and tokens (retrieved from the login module)
app_key = l.api_key  # API key for the Breeze API
secret_key = l.api_secret  # Secret key for generating secure checksums
session_token = l.session_key  # Session token for user authentication

# Define the request body (input parameters for API call)
# This request body specifies the exchange, date range, and the underlying asset for the API query
body = {
    "exchange_code": "NSE",  # Exchange (NSE in this case)
    "from_date": "2023-03-12T04:00:00.000Z",  # Start date in ISO 8601 format
    "to_date": "2023-03-12T04:00:00.000Z",  # End date in ISO 8601 format
    "underlying": "IDECEL",  # Underlying asset symbol
    "portfolio_type": ""  # Portfolio type, left blank in this example
}

# Convert the request body to JSON format (used in checksum generation)
payload_for_checksum = json.dumps(body, separators=(',', ':'))

# Generate the request headers
# This includes creating the checksum to ensure data integrity and security
current_date = datetime.utcnow().isoformat()[:19] + '.000Z'  # Get the current UTC date-time in the required format
checksum = hashlib.sha256((current_date + payload_for_checksum + secret_key).encode("utf-8")).hexdigest()  # Create a SHA-256 checksum

# Set up the headers for the API request, including the checksum, timestamp, and authentication details
headers = {
    "Content-Type": "application/json",  # Specifies that the request body is in JSON format
    'X-Checksum': "token " + checksum,  # Custom header for secure checksum
    'X-Timestamp': current_date,  # Custom header for the current timestamp
    'X-AppKey': app_key,  # Custom header for the API key
    'X-SessionToken': session_token  # Custom header for the session token
}

# Convert the request body to JSON format to be sent as a payload in the request
payload = json.dumps(body)

# Set up the connection to the Breeze API server using HTTPS
conn = http.client.HTTPSConnection("api.icicidirect.com")

# Send the GET request to the API endpoint '/breezeapi/api/v1/portfolioholdings'
# The request includes the payload (request body) and the headers for authentication
conn.request("GET", "/breezeapi/api/v1/portfolioholdings", payload, headers)

# Get the API response
res = conn.getresponse()

# Read the response data
data = res.read()

# Print the API response (decoded from bytes to a string)
print(data.decode("utf-8"))
