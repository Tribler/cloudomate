from bs4 import BeautifulSoup as soup
import urllib


def extract_info(url):
    """
    Extracts amount and BitCoin address from a Coinbase URL.
    :param url: the Coinbase URL like "https://www.coinbase.com/checkouts/2b30a03995ec62f15bdc54e8428caa87"
    :return: a tuple of the amount in BitCoin along with the address
    """
    response = urllib.urlopen(url)
    site = soup(response)
    details = site.find('div', {'class': 'details'})
    bitcoin_url = details.p.a['href']
    # bitcoin:1HhFxARoW7Pfzgzm2ar9xL1PHUu4L3RbaR?amount=0.00045748&amp;r=https://www.coinbase.com/r/59240ff201bc8b1054a037e5
    address = extract_address(bitcoin_url)
    amount = extract_amount(bitcoin_url)

    return amount, address


def extract_amount(bitcoin_url):
    '''
    Extract amount from bitcoin url
    :param bitcoin_url: bitcoin url
    :return: Amount to be transferred
    '''
    amount_section, _ = bitcoin_url.split('&')
    amount_text = amount_section.split('=')[1]
    amount = float(amount_text)
    return amount

def extract_address(bitcoin_url):
    '''
    Extract address from bitcoin url
    :param bitcoin_url: bitcoin url
    :return: Bitcoin address
    '''
    address, _ = bitcoin_url.split('?')
    address = address.split(':')[1]
    if not is_btc_address(address):
        raise ValueError('Address is not a bitcoin address: {0}'.format(address))
    return address


def is_btc_address(address):
    '''
    TODO see if there is a better check
    Check if address is a valid bitcoin address
    :param address: address
    :return: 
    '''
    return len(address) == 34 and address.isalnum()