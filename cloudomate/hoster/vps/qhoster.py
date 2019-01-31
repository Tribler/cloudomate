from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import super

from future import standard_library

from cloudomate.gateway.coinify import Coinify
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.vps_hoster import VpsOption

standard_library.install_aliases()


class QHoster(SolusvmHoster):
    CART_URL = 'https://www.qhoster.com/clients/cart.php?a=view'

    TUN_TAP_SETTINGS = False

    def __init__(self, settings):
        super(QHoster, self).__init__(settings)

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_clientarea_url():
        return 'https://www.qhoster.com/clients/clientarea.php'

    @staticmethod
    def get_gateway():
        return Coinify

    @staticmethod
    def get_metadata():
        return 'qhoster', 'https://www.qhoster.com/'

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
        browser.open("https://www.qhoster.com/linux-vps.html")
        options = cls._parse_openvz_hosting(browser.get_current_page())
        return list(options)

    def purchase(self, wallet, option):
        self._browser.open(option.purchase_url)
        self._browser.select_form('form#orderfrm')
        self._fill_server_form()
        form = self._browser.get_current_form()
        form['configoption[3]'] = '1036'  # Ubuntu 16.04
        self._browser.submit_selected()
        response_text = self._browser.get_current_page().text.strip()
        if response_text:
            print(response_text)
            return

        self._browser.open(self.CART_URL)
        self._browser.select_form(selector='form#frmCheckout')
        self._fill_user_form(self.get_gateway().get_name())
        self._browser.select_form('form#myForm')
        self._browser.submit_selected()
        return self.pay(wallet, self.get_gateway(), self._browser.get_url())

    '''
    Hoster-specific methods that are needed to perform the actions
    '''

    @classmethod
    def _parse_openvz_hosting(cls, page):
        openvz = page.find('div', {'id': 'tab1'})
        options = openvz.find_all('aside', {'class': 'plan1'})
        for option in options:
            first_price_option = option.find('select', {'class': 'field2'}).find('option')
            yield VpsOption(
                name=option.find('h3').text.strip(),
                storage=int(option.find('li', {'class': 'icon3'}).text.split(' ')[0]),
                cores=int(option.find('li', {'class': 'icon2'}).text.split(' ')[0]),
                memory=int(option.find('li', {'class': 'icon6'}).text.split(' ')[0]),
                bandwidth=int(option.find('li', {'class': 'icon4'}).text.split(' ')[0]),
                connection=int(option.find('li', {'class': 'icon5'}).text.split(' ')[0]),
                price=float(first_price_option.text.split('$')[1].split('/')[0]),
                purchase_url=first_price_option['value']
            )
