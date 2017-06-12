import json
import urllib

name = 'bitpay'


def extract_info(url):
    """
    Extracts amount and BitCoin address from a BitPay URL.
    :param url: the BitPay URL like "https://bitpay.com/invoice?id=J3qU6XapEqevfSCW35zXXX"
    :return: a tuple of the amount in BitCoin along with the address
    """
    bitpay_id = url.split("=")[1]
    url = "https://bitpay.com/invoiceData/" + bitpay_id + "?poll=false"
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    amount = float(data['invoice']['buyerTotalBtcAmount'])
    address = data['invoice']['bitcoinAddress']
    return amount, address


# https://bitpay.com/pricing
GATEWAY_FEE = 0.01


def estimate_price(cost):
    return cost * (1.0 + GATEWAY_FEE)
