"""
This code shows how to retrieve buy and sell prices
from the Coinbase Data API using the Python requests package.
Then, the code prints the collected information in human-readable format.
"""

import argparse as ap
import requests

parser = ap.ArgumentParser()
parser.add_argument('--currency', type=str, help='Currency code')
args = parser.parse_args()

host = 'https://api.coinbase.com/v2'
currency = args.currency
buy_endpoint = f'/prices/BTC-{currency}/buy'
sell_endpoint = f'/prices/BTC-{currency}/sell'

response = requests.get(host + buy_endpoint)

if response.status_code == 200:
    # Successfully received a response from the endpoint
    # Use the json() method to convert the response body to a Python dictionary.
    buy_dict = response.json()
    buy_price = buy_dict['data']['amount']
    print(f'The buy price in {currency} is: {buy_price}')
else:
    # Something went wrong with the request
    print(f'Error: {currency} not found')

response = requests.get(host + sell_endpoint)

if response.status_code == 200:
    # Successfully received a response from the endpoint
    # Use the json() method to convert the response body to a Python dictionary.
    sell_dict = response.json()
    sell_price = sell_dict['data']['amount']
    print(f'The sell price in {currency} is: {sell_price}')
else:
    # Something went wrong with the request
    print(f'Error: {currency} not found')


    