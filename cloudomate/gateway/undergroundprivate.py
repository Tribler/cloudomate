from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
from mechanicalsoup import StatefulBrowser
from fake_useragent import UserAgent
from future import standard_library

from cloudomate.gateway.gateway import Gateway, PaymentInfo

standard_library.install_aliases()
if sys.version_info > (3, 0):
    from urllib.request import urlopen
else:
    from urllib2 import urlopen


class UndergroundPrivate(Gateway):
    @staticmethod
    def get_name():
        return "SpectroCoin"

    @classmethod
    def extract_info(cls, url):
        """
        Extracts amount and BitCoin address from a UndergroundPrivate payment URL.
        :param url: the URL like https://spectrocoin.com/en/order/view/1045356-0X6XzpZi.html
        :return: a tuple of the amount in BitCoin along with the address
        """
        user_agent = UserAgent(fallback="Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0")
        browser = StatefulBrowser(user_agent=user_agent.random)
        browser.open(url)
        soup = browser.get_current_page()

        amount = soup.select_one('div.payAmount').text.split(" ")[0]
        address = soup.select_one('div.address').text
        return PaymentInfo(float(amount), address)

    @staticmethod
    def get_gateway_fee():
        return 0.0
