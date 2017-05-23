import json
import urllib


def extract_info(url):
    """
    Extracts amount and BitCoin address from a Coinbase URL.
    :param url: the Coinbase URL like "https://www.coinbase.com/checkouts/2b30a03995ec62f15bdc54e8428caa87"
    :return: a tuple of the amount in BitCoin along with the address
    """
    bitpay_id = url.split("=")[1]
    url = "https://bitpay.com/invoiceData/" + bitpay_id + "?poll=false"
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    amount = data['invoice']['buyerTotalBtcAmount']
    address = data['invoice']['bitcoinAddress']
    return amount, address
