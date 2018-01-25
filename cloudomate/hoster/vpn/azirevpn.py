# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import sys
from builtins import round

import requests
from forex_python.converter import CurrencyRates
from future import standard_library

from cloudomate.gateway.bitpay import BitPay
from cloudomate.hoster.vpn.vpn_hoster import VpnHoster, VpnOption, VpnStatus, VpnConfiguration

standard_library.install_aliases()


class AzireVpn(VpnHoster):
    REGISTER_URL = "https://manager.azirevpn.com/en/auth/register"
    CONFIGURATION_URL = "https://www.azirevpn.com/support/configuration/generate?os=others&country=se1&nat=0&keys=0&protocol=udp&tls=gcm&port=random"
    LOGIN_URL = "https://manager.azirevpn.com/auth/login"
    ORDER_URL = "https://manager.azirevpn.com/order"
    OPTIONS_URL = "https://www.azirevpn.com"
    DASHBOARD_URL = "https://manager.azirevpn.com"

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
        soup = browser.get_current_page()
        strong = soup.select_one("div.prices > ul > li:nth-of-type(2) > ul > li:nth-of-type(1) strong")
        string = strong.get_text()

        # Calculate the price in USD
        eur = float(string[string.index("€") + 2: string.index("/") - 1])
        price = round(CurrencyRates().convert("EUR", "USD", eur), 2)

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
        self.pay(wallet, self.get_gateway(), page.url)

    '''
    Hoster-specific methods that are needed to perform the actions
    '''

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
        form["payment_gateway"] = "bitpay"
        form["tos"] = True
        page = self._browser.submit_selected()

        return page
