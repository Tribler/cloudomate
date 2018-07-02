# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import sys
from builtins import round

import requests
from currency_converter import CurrencyConverter
from future import standard_library

from cloudomate.gateway.bitpay import BitPay
from cloudomate import wallet as wallet_util
from cloudomate.hoster.vpn.vpn_hoster import VpnHoster, VpnOption, VpnStatus, VpnConfiguration

standard_library.install_aliases()


class AzireVpn(VpnHoster):
    REGISTER_URL = "https://www.azirevpn.com/en/manager/auth/register"
    CONFIGURATION_URL = "https://www.azirevpn.com/cfg/openvpn/generate?os=others&country=se1&nat=0&keys=0&protocol=udp&tls=gcm&port=random"
    LOGIN_URL = "https://www.azirevpn.com/manager/auth/login"
    ORDER_URL = "https://www.azirevpn.com/manager/order"
    OPTIONS_URL = "https://www.azirevpn.com"
    DASHBOARD_URL = "https://www.azirevpn.com/manager"

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_gateway():
        return BitPay

    @staticmethod
    def get_metadata():
        return "AzireVPN", "https://www.azirevpn.com/"

    @staticmethod
    def get_required_settings():
        return {"user": ["username", "password"]}

    '''
    Action methods of the Hoster that can be called
    '''

    def get_configuration(self):
        response = requests.get(self.CONFIGURATION_URL)
        ovpn = response.text
        return VpnConfiguration(self._settings.get("user", "username"),
                                self._settings.get("user", "password"), ovpn)

    @classmethod
    def get_options(cls):
        # Get string with price from the website
        browser = cls._create_browser()
        browser.open(cls.OPTIONS_URL)
        soup = browser.get_current_page().find_all('strong')
        string = str(soup)
        words = string.split()

        # Calculate the price in USD
        eur = float(words[2])
        c = CurrencyConverter()
        price = round(c.convert(eur, "EUR", "USD"), 2)

        name, _ = cls.get_metadata()
        option = VpnOption(name, "OpenVPN", price, sys.maxsize, sys.maxsize)
        return [option]

    def get_status(self):
        self._login()

        # Retrieve the expiration date
        self._browser.open(self.DASHBOARD_URL)
        soup = self._browser.get_current_page()
        time = soup.select_one("div.dashboard time")
        date = time["datetime"]

        # Parse the expiration date
        date = date[0:-3] + date[-2:]  # Remove colon (:) in timezone
        expiration = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")

        # Determine the status
        now = datetime.datetime.now(datetime.timezone.utc)
        online = False
        if now <= expiration:
            online = True
        return VpnStatus(online, expiration)

    def purchase(self, wallet, option):
        # Prepare for the purchase on the AzireVPN website
        self._register()
        self._login()
        page = self._order()

        # Make the payment
        return self.pay(wallet, page.url)

    '''
    Hoster-specific methods that are needed to perform the actions
    '''

    def pay(self, wallet, url):

        self._browser.open(url)
        soup = self._browser.get_current_page()
        address = soup.select_one("div.transaction > input").get("value")
        amount = float(soup.select_one("div.transaction > input:nth-of-type(2)").get("value"))
        fee = wallet_util.get_network_fee()
        print(('Calculated fee: %s' % fee))
        transaction_hash = wallet.pay(address, amount, fee)
        print('Done purchasing')
        return transaction_hash



    def _register(self):
        self._browser.open(self.REGISTER_URL)
        form = self._browser.select_form()
        form["username"] = self._settings.get("user", "username")
        form["password"] = self._settings.get("user", "password")
        form["password_confirmation"] = self._settings.get("user", "password")
        page = self._browser.submit_selected()

        if page.url == self.REGISTER_URL:
            # An error occurred
            soup = self._browser.get_current_page()
            ul = soup.select_one("ul.alert-danger")
            print(ul.get_text())
            sys.exit(2)

        return page

    def _login(self):
        self._browser.open(self.LOGIN_URL)
        form = self._browser.select_form()
        form["username"] = self._settings.get("user", "username")
        form["password"] = self._settings.get("user", "password")
        page = self._browser.submit_selected()

        if page.url == self.LOGIN_URL:
            # An error occurred
            soup = self._browser.get_current_page()
            ul = soup.select_one("ul.alert-danger")
            print(ul.get_text())
            sys.exit(2)

        return page

    def _order(self):
        self._browser.open(self.ORDER_URL)
        form = self._browser.select_form("form#orderForm")
        form["package"] = "1"
        form["payment_gateway"] = "coinpayment"
        form["coinpayment_crypto"] = "BTC"
        form["tos"] = True
        page = self._browser.submit_selected()

        return page
