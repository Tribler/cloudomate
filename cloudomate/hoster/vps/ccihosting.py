from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import sys
from builtins import int
from builtins import super

from future import standard_library

from cloudomate.gateway.coinpayments import CoinPayments
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.vps_hoster import VpsOption
from cloudomate.hoster.vps.vps_hoster import VpsStatus
from cloudomate.hoster.vps.vps_hoster import VpsStatusResource

standard_library.install_aliases()


class CCIHosting(SolusvmHoster):
    CART_URL = 'https://www.ccihosting.com/accounts/cart.php?a=confdomains'
    OPTIONS_URL = 'https://www.ccihosting.com/offshore-vps.html'

    # true if you can enable tuntap in the control panel
    TUN_TAP_SETTINGS = False

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_clientarea_url():
        return 'https://www.ccihosting.com/accounts/clientarea.php'

    @staticmethod
    def get_gateway():
        return CoinPayments

    @staticmethod
    def get_metadata():
        return 'CCIHosting', 'https://www.ccihosting.com/'

    @staticmethod
    def get_required_settings():
        return {
            'user': ['firstname', 'lastname', 'email', 'phonenumber', 'password'],
            'address': ['address', 'city', 'state', 'zipcode', 'countrycode'],
            'server': ['hostname', 'root_password', 'ns1', 'ns2']
        }

    '''
    Action methods of the Hoster that can be called
    '''

    @classmethod
    def get_options(cls):
        browser = cls._create_browser()
        browser.open(cls.OPTIONS_URL)
        return list(cls._parse_options(browser.get_current_page()))


    def purchase(self, wallet, option):
        self._browser.open(option.purchase_url)
        self._server_form()
        self._browser.open(self.CART_URL)

        summary = self._browser.get_current_page().find('div', class_='summary-container')
        self._browser.follow_link(summary.find('a', class_='btn-checkout'))

        try:
            self._browser.select_form(selector='form#frmCheckout')
        except LinkNotFoundError:
            print("Too many open transactions, try connecting from a different IP")
            raise

        self._fill_user_form(self.get_gateway().get_name())

        self._browser.select_form(nr=0)  # Go to payment form
        self._browser.submit_selected()

        return self.pay(wallet, self.get_gateway(), self._browser.get_url(), self._browser, self._settings)
        # self._browser.open(option.purchase_url)
        # self._server_form()  # Add item to cart
        # self._browser.open(self.CART_URL)

        # summary = self._browser.get_current_page().find('div', class_='summary-container')
        # self._browser.follow_link(summary.find('a', class_='btn-checkout'))

        # self._browser.select_form(selector='form[name=orderfrm]')
        # self._fill_user_form(self.get_gateway().get_name())

        # coinpayments_url = self._browser.get_current_page().find('form')['action']
        # self._browser.select_form('form[action="' + coinpayments_url + '"]')
        # self._browser.get_current_form().print_summary()

        # response = self._browser.submit_selected()
        # print(response.text)

        # print("--- \n\n---\n")

        # print(self._browser.get_current_page())
        # # coinpayments_url = "https://www.ccihosting.com/accounts/cart.php?a=complete"
        # return self.pay(wallet, self.get_gateway(), coinpayments_url)

    '''
    Hoster-specific methods that are needed to perform the actions
    '''

    @staticmethod
    def _convert_gigabyte(number, unit):
        u = unit.lower()
        n = float(number)
        if u == 'kb':
            n /= 1024.0 * 1024.0
        elif u == 'mb':
            n /= 1024.0
        elif u == 'gb':
            pass
        elif u == 'tb':
            n *= 1024.0
        else:
            raise ValueError('Unknown unit {}'.format(u))

        return n

    def _server_form(self):
        """
        Using a form does not work for some reason, so use post request instead
        """
        self._browser.post('https://www.ccihosting.com/accounts/cart.php', {
            'ajax': '1',
            'a': 'confproduct',
            'configure': 'true',
            'i': '0',
            'billingcycle': 'monthly',
            'hostname': self._settings.get('server', 'hostname'),
            'rootpw': self._settings.get('server', 'root_password'),
            'ns1prefix': self._settings.get('server', 'ns1'),
            'ns2prefix': self._settings.get('server', 'ns2'),
            'configoption[214]': '1193',  # Ubuntu 16.04
            'configoption[258]': '955',
        })

    @classmethod
    def _parse_options(cls, page):
        tables = page.findAll('div', class_='pricing')
        for column in tables:
            yield cls._parse_cci_options(column)

    @staticmethod
    def _parse_cci_options(column):
        header = column.find('div', class_='phead')
        price = column.find('span', class_='starting-price')
        info = column.find('ul').findAll('li')
        try:
            url=column.find('a')['onclick'].split("'")[3]
        except KeyError:
            url=column.find('a')['href']
        return VpsOption(
            name=header.find('h2').contents[0],
            price=float(price.contents[0]),
            cores=int(info[1].find('strong').contents[0]),
            memory=float(info[2].find('strong').contents[0]),
            storage=float(info[3].find('strong').contents[0]),
            bandwidth=sys.maxsize,
            connection=0.01,  # See FAQ at https://www.ccihosting.com/offshore-vps.html
            # purchase_url=column.find('a')['onclick']
            purchase_url=url
        )
