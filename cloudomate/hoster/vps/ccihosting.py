from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import sys
from builtins import int
from builtins import super

from future import standard_library

from cloudomate.gateway.coinbase import Coinbase
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.vps_hoster import VpsOption
from cloudomate.hoster.vps.vps_hoster import VpsStatus
from cloudomate.hoster.vps.vps_hoster import VpsStatusResource

standard_library.install_aliases()


class CCIHosting(SolusvmHoster):
    CART_URL = 'https://www.ccihosting.com/accounts/cart.php?a=confdomains'
    OPTIONS_URL = 'https://www.ccihosting.com/offshore-vps.html'

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_clientarea_url():
        return 'https://www.ccihosting.com/accounts/clientarea.php'

    @staticmethod
    def get_gateway():
        return Coinbase

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

    def get_status(self):
        status = super().get_status()

        # Usage
        page = self._browser.open(status.clientarea.url)
        matches = re.findall(r'([\d.]+) (KB|MB|GB|TB) of ([\d.]+) (KB|MB|GB|TB) Used', page.text)
        usage = (
            self._convert_gigabyte(matches[1][0], matches[1][1]),  # Memory used
            self._convert_gigabyte(matches[1][2], matches[1][3]),  # Memory total
            self._convert_gigabyte(matches[0][0], matches[0][1]),  # Storage used
            self._convert_gigabyte(matches[0][2], matches[0][3]),  # Storage total
            self._convert_gigabyte(matches[2][0], matches[2][1]),  # Bandwidth used
            self._convert_gigabyte(matches[2][2], matches[2][3])  # Bandwidth total
        )

        memory = VpsStatusResource(usage[0], usage[1])
        storage = VpsStatusResource(usage[2], usage[3])
        bandwidth = VpsStatusResource(usage[4], usage[5])

        # return status
        return VpsStatus(memory, storage, bandwidth, status.online, status.expiration, status.clientarea)

    def purchase(self, wallet, option):
        self._browser.open(option.purchase_url)
        self._server_form()  # Add item to cart
        self._browser.open(self.CART_URL)

        summary = self._browser.get_current_page().find('div', class_='summary-container')
        self._browser.follow_link(summary.find('a', class_='btn-checkout'))

        self._browser.select_form(selector='form[name=orderfrm]')
        self._fill_user_form(self.get_gateway().get_name())

        coinbase_url = self._browser.get_current_page().find('form')['action']
        self.pay(wallet, self.get_gateway(), coinbase_url)

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
        tables = page.findAll('div', class_='p_table')
        for column in tables:
            yield cls._parse_cci_options(column)

    @staticmethod
    def _parse_cci_options(column):
        header = column.find('div', class_='phead')
        price = column.find('span', class_='starting-price')
        info = column.find('ul').findAll('li')
        return VpsOption(
            name=header.find('h2').contents[0],
            price=float(price.contents[0]),
            cores=int(info[1].find('strong').contents[0]),
            memory=float(info[2].find('strong').contents[0]),
            storage=float(info[3].find('strong').contents[0]),
            bandwidth=sys.maxsize,
            connection=0.01,  # See FAQ at https://www.ccihosting.com/offshore-vps.html
            purchase_url=column.find('a')['href']
        )
