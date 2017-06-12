import urllib

from bs4 import BeautifulSoup

name = 'coinbase'


def extract_info(url):
    """
    Extracts amount and BitCoin address from a Coinbase URL.
    :param url: the Coinbase URL like "https://www.coinbase.com/checkouts/2b30a03995ec62f15bdc54e8428caa87"
    :return: a tuple of the amount in BitCoin along with the address
    """
    response = urllib.urlopen(url)
    site = BeautifulSoup(response, 'lxml')
    details = site.find('div', {'class': 'details'})
    bitcoin_url = details.p.a['href']
    # bitcoin:1HhFxARoW7Pfzgzm2ar9xL1PHUu4L3RbaR?amount=0.00045748&amp;r=https://www.coinbase.com/r/59240ff201bc8b1054a037e5
    address = extract_address(bitcoin_url)
    amount = extract_amount(bitcoin_url)

    return amount, address


def extract_amount(bitcoin_url):
    """
    Extract amount from bitcoin url
    :param bitcoin_url: bitcoin url
    :return: Amount to be transferred
    """
    amount_section, _ = bitcoin_url.split('&')
    amount_text = amount_section.split('=')[1]
    amount = float(amount_text)
    return amount


def extract_address(bitcoin_url):
    """
    Extract address from bitcoin url
    :param bitcoin_url: bitcoin url
    :return: Bitcoin address
    """
    address_text, _ = bitcoin_url.split('?')
    address = address_text.split(':')[1]
    return address


# https://support.coinbase.com/customer/portal/articles/1277919-what-fees-does-coinbase-charge-for-merchant-processing-
GATEWAY_FEE = 0.01


def estimate_price(cost):
    return cost * (1.0 + GATEWAY_FEE)
