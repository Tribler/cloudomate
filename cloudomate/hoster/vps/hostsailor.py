from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
from builtins import super

from future import standard_library

from cloudomate.gateway.coingate import CoinGate
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.vps_hoster import VpsOption

standard_library.install_aliases()


class HostSailor(SolusvmHoster):
    # true if you can enable tuntap in the control panel
    TUN_TAP_SETTINGS = False

    def __init__(self, settings):
        super(HostSailor, self).__init__(settings)

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_clientarea_url():
        return 'https://clients.hostsailor.com/clientarea.php'

    @staticmethod
    def get_gateway():
        return CoinGate

    @staticmethod
    def get_metadata():
        return 'hostsailor', 'https://hostsailor.com'

    @staticmethod
    def get_required_settings():
        return {
            'user': ['firstname', 'lastname', 'email', 'phonenumber', 'password'],
            'address': ['address', 'city', 'state', 'zipcode'],
        }

    '''
    Action methods of the Hoster that can be called
    '''

    @classmethod
    def get_options(cls):
        browser = cls._create_browser()
        browser.open("https://hostsailor.com/vps-hosting/openvz-ssd-vps/")
        options = cls._parse_openvz_ssd_hosting(browser.get_current_page())
        return list(options)

    @classmethod
    def _parse_openvz_ssd_hosting(cls, page):
        options = page.find_all('div', {'class': 'crumina-pricing-tables-item'})
        for option in options:
            price_usd = float(option.find('h2', {'class': 'rate'}).text[1:])
            list_elements = option.find_all('li', {'class': 'position-item'})
            yield VpsOption(
                name=option.find('h5', {'class': 'pricing-title'}).text.strip(),
                storage=list_elements[2].text.strip().split(' ')[2],
                cores=list_elements[5].text.strip().split(' ')[1],
                memory=cls.parse_memory(list_elements[0]),
                bandwidth=cls.parse_bandwidth(list_elements[8]),
                connection=list_elements[9].text.strip().split(' ')[2].replace('Gbit', ''),
                price=price_usd,
                purchase_url=option.find('a', {'class', 'btn'})['href']
            )

    @staticmethod
    def parse_memory(memory):
        amount = memory.text.strip().split(' ')[1]
        if amount.endswith('MB'):
            return int(amount.replace('MB', '')) / 1000
        else:
            return int(amount.replace('GB', ''))

    @staticmethod
    def parse_bandwidth(bandwidth):
        amount = bandwidth.text.strip().split(' ')[1]
        if amount.endswith('GB'):
            return int(amount.replace('GB', '')) / 1000
        else:
            return int(amount.replace('TB', ''))

    def purchase(self, wallet, option):
        self._browser.open(option.purchase_url)
        self._server_form()
        self._browser.open('https://clients.hostsailor.com/cart.php?a=view')
        link = self._browser.get_current_page().find('a', {'id': 'checkout'})
        self.get_browser().follow_link(link)

        form = self._browser.select_form(selector='form#frmCheckout')
        form['customfield[96]'] = 'Google'
        self._fill_user_form(self.get_gateway().get_name())
        payment_link = self._browser.get_current_page().find('form')['action']
        print("Payment link: " + payment_link)
        return self.pay(wallet, self.get_gateway(), payment_link)

    '''
    Hoster-specific methods that are needed to perform the actions
    '''

    def _server_form(self):
        """
        Fills in the form containing server configuration.
        :return:
        """
        form = self._browser.select_form('form#frmConfigureProduct')
        self._fill_server_form()
        form['configoption[560]'] = '8168'  # Ubuntu 16.04
        self._browser.submit_selected()
        page = self._browser.get_current_page()
        if page.find('li'):
            print(page.text)
            sys.exit(2)
