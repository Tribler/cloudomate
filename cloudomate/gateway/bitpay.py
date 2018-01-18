import json
import urllib.error
import urllib.parse
import urllib.request

name = 'bitpay'


def extract_info(url):
    """
    Extracts amount and BitCoin address from a BitPay URL.
    :param url: the BitPay URL like "https://bitpay.com/invoice?id=J3qU6XapEqevfSCW35zXXX"
    :return: a tuple of the amount in BitCoin along with the address
    """
    bitpay_id = url.split("=")[1]
    url = "https://bitpay.com/invoices/" + bitpay_id
    response = urllib.request.urlopen(url)
    response = json.loads(response.read().decode('utf-8'))
    amount = float(response['data']['btcDue'])
    address = response['data']['bitcoinAddress']
    return amount, address


# https://bitpay.com/pricing
GATEWAY_FEE = 0.01


def estimate_price(cost):
    return cost * (1.0 + GATEWAY_FEE)
