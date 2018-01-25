from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys

from bs4 import BeautifulSoup
from future import standard_library

from cloudomate.gateway.gateway import Gateway, PaymentInfo

standard_library.install_aliases()
if sys.version_info > (3, 0):
    from urllib.request import urlopen
else:
    from urllib2 import urlopen


class Coinbase(Gateway):
    @staticmethod
    def get_name():
        return "coinbase"

    @classmethod
    def extract_info(cls, url):
        """
        Extracts amount and BitCoin address from a Coinbase URL.
        :param url: the Coinbase URL like "https://www.coinbase.com/checkouts/2b30a03995ec62f15bdc54e8428caa87"
        :return: a tuple of the amount in BitCoin along with the address
        """
        response = urlopen(url)
        site = BeautifulSoup(response, 'lxml')
        details = site.find('div', {'class': 'details'})
        bitcoin_url = details.p.a['href']
        # bitcoin:1HhFxARoW7Pfzgzm2ar9xL1PHUu4L3RbaR?amount=0.00045748&amp;r=https://www.coinbase.com/r/59240ff201bc8b1054a037e5
        address = cls._extract_address(bitcoin_url)
        amount = cls._extract_amount(bitcoin_url)

        return PaymentInfo(amount, address)

    @staticmethod
    def get_gateway_fee():
        """Get the coinbase gateway fee.

        See: https://support.coinbase.com/customer/portal/articles/1277919-what-fees-does-coinbase-charge-for-merchant-processing

        :return: The coinbase gateway fee
        """
        return 0.01

    @staticmethod
    def _extract_amount(bitcoin_url):
        """
        Extract amount from bitcoin url
        :param bitcoin_url: bitcoin url
        :return: Amount to be transferred
        """
        amount_section, _ = bitcoin_url.split('&')
        amount_text = amount_section.split('=')[1]
        amount = float(amount_text)
        return amount

    @staticmethod
    def _extract_address(bitcoin_url):
        """
        Extract address from bitcoin url
        :param bitcoin_url: bitcoin url
        :return: Bitcoin address
        """
        address_text, _ = bitcoin_url.split('?')
        address = address_text.split(':')[1]
        return address
