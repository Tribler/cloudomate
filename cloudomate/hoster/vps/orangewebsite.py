from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import re
import sys
from builtins import round
from builtins import super

from currency_converter import CurrencyConverter
from future import standard_library
from mechanicalsoup.utils import LinkNotFoundError

from cloudomate.gateway.coinpayments import CoinPayments
from cloudomate.hoster.vps.clientarea import ClientArea
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.vps_hoster import VpsOption

standard_library.install_aliases()


class OrangeWebsite(SolusvmHoster):
    CART_URL = 'https://secure.orangewebsite.com/cart.php?a=view'

    # true if you can enable tuntap in the control panel
    TUN_TAP_SETTINGS = True

    _settings = None
    _controlpanel = None

    def __init__(self, settings):
        super(OrangeWebsite, self).__init__(settings)

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_clientarea_url():
        return 'https://secure.orangewebsite.com/clientarea.php'

    @staticmethod
    def get_gateway():
        return CoinPayments

    @staticmethod
    def get_metadata():
        return 'orangewebsite', 'https://www.orangewebsite.com/'

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
        """
        Linux (OpenVZ) and Windows (KVM) pages are slightly different, therefore their pages are parsed by different
        methods. Windows configurations allow a selection of Linux distributions, but not vice-versa.
        :return: possible configurations.
        """
        browser = cls._create_browser()
        browser.open("https://www.orangewebsite.com/vps.php")
        options = cls._parse_openvz_hosting(browser.get_current_page())
        lst = list(options)

        return lst

    def purchase(self, wallet, option):
        self._browser.open(option.purchase_url)
        self._server_form()

        self._browser.open(self.CART_URL)
        self._cart_form()

        self._browser.select_form(nr=0)  # Go to payment form
        self._browser.submit_selected()

        return self.pay(wallet, self.get_gateway(), self._browser.get_url(), self._browser, self._settings)

    '''
    Hoster-specific methods that are needed to perform the actions
    '''

    def _server_form(self):
        """
        Fills in the form containing server configuration.
        :return:
        """
        form = self._browser.select_form('form#orderfrm')

        form['configoption[6]'] = '1127'  # Ubuntu 16.04
        form.set("ajax", 1, force=True)

        # checkout = self._browser.get_current_page().find("input", {"value": "Checkout"})

        self._browser.submit_selected()

    def _cart_form(self):
        form = self._browser.select_form('form#mainfrm')

        form['email'] = self._change_email_provider(self._settings.get('user', "email"), '@gmail.com')
        form['password'] = self._settings.get('user', "password")
        form['password2'] = self._settings.get('user', "password")
        form['paymentmethod'] = 'coinpayments'

        form['accepttos'] = True

        # Default submit button is "Validate code", use "Complete order" instead
        soup = self._browser.get_current_page()
        submit = soup.select_one('input.ordernow')
        form.choose_submit(submit)

        self._browser.submit_selected()


    @classmethod
    def _parse_openvz_hosting(cls, page):
        options = page.find_all('li', {'class': 'virtual'})
        for idx, option in enumerate(options, start=1):
            list_elements = option.find_all('span', {"class": "right"})
            price_eur = float(option.find('span', {'class', 'price_figure'}).text[1:])
            c = CurrencyConverter()
            price_usd = round(c.convert(price_eur, 'EUR', 'USD'), 2)
            yield VpsOption(
                name=option.find('h3').text.strip().replace("Virtual Server - ", ""),
                storage=list_elements[1].text.strip().split(' ')[0][:-2],
                cores=list_elements[2].text.strip().split(' ')[0],
                memory=float(list_elements[0].text.strip().split(' ')[0][:-2])/1024,
                bandwidth=list_elements[3].text.strip().split(' ')[0][:-2],
                connection=1,
                price=price_usd,
                purchase_url=option.find_all('a', {'class': 'action_button'})[1]['href'],
            )

    def change_root_password(self, new_password):
        self._create_controlpanel()
        return self._controlpanel.change_root_password(new_password)

    def get_status_control_panel(self):
        self._create_controlpanel()
        return self._controlpanel.get_status()

