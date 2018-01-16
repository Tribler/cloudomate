import urllib.request

from cloudomate.hoster.vpn.vpn_hoster import VpnHoster
from cloudomate.hoster.vpn.vpn_hoster import VpnStatus
from cloudomate.hoster.vpn.vpn_hoster import VpnInfo
from cloudomate.gateway import bitpay
from cloudomate import wallet as wallet_util
from forex_python.converter import CurrencyRates
import sys
import datetime


class AzireVpn(VpnHoster):
    REGISTER_URL = "https://manager.azirevpn.com/en/auth/register"
    INFO_URL = "https://www.azirevpn.com/support/configuration/generate?os=others&country=se1&nat=0&keys=0&protocol=udp&tls=gcm&port=random"
    LOGIN_URL = "https://manager.azirevpn.com/auth/login"
    ORDER_URL = "https://manager.azirevpn.com/order"
    OPTIONS_URL = "https://www.azirevpn.com"
    DASHBOARD_URL = "https://manager.azirevpn.com"

    required_settings = [
        'username',
        'password',
    ]

    def __init__(self):
        super().__init__()

        self.name = "AzireVPN"
        self.website = "https://www.azirevpn.com"
        self.protocol = "OpenVPN"
        self.bandwidth = sys.maxsize
        self.speed = sys.maxsize

        self.gateway = bitpay

    def options(self):
        self._browser.open(self.OPTIONS_URL)
        soup = self._browser.get_current_page()
        strong = soup.select_one("div.prices > ul > li:nth-of-type(2) > ul > li:nth-of-type(1) strong")
        string = strong.get_text()
        eur = float(string[string.index("€") + 2: string.index("/") - 1])
        self.price = round(CurrencyRates().convert("EUR", "USD", eur), 2)

        return super().options()

    def purchase(self, user_settings, wallet):
        # Prepare for the purchase on the AzireVPN website
        self._register(user_settings)
        self._login(user_settings)
        page = self._order(user_settings, wallet)

        # Make the payment
        print("Purchasing AzireVPN instance")
        amount, address = self.gateway.extract_info(page.url)
        print(('Paying %s BTC to %s' % (amount, address)))
        fee = wallet_util.get_network_fee()
        print(('Calculated fee: %s' % fee))
        transaction_hash = wallet.pay(address, amount, fee)
        print('Done purchasing')
        return transaction_hash

    def info(self, user_settings):
        response = urllib.request.urlopen(self.INFO_URL)
        ovpn = response.read().decode('utf-8')
        return VpnInfo(user_settings.get("username"), user_settings.get("password"), ovpn)

    def status(self, user_settings):
        self._login(user_settings)

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

    def _register(self, user_settings):
        self._browser.open(self.REGISTER_URL)
        form = self._browser.select_form()
        form["username"] = user_settings.get("username")
        form["password"] = user_settings.get("password")
        form["password_confirmation"] = user_settings.get("password")
        page = self._browser.submit_selected()

        if page.url == self.REGISTER_URL:
            # An error occurred
            soup = self._browser.get_current_page()
            ul = soup.select_one("ul.alert-danger")
            print(ul.get_text())
            sys.exit(2)

        return page

    def _login(self, user_settings):
        self._browser.open(self.LOGIN_URL)
        form = self._browser.select_form()
        form["username"] = user_settings.get("username")
        form["password"] = user_settings.get("password")
        page = self._browser.submit_selected()

        if page.url == self.LOGIN_URL:
            # An error occurred
            soup = self._browser.get_current_page()
            ul = soup.select_one("ul.alert-danger")
            print(ul.get_text())
            sys.exit(2)

        return page

    def _order(self, user_settings, wallet):
        self._browser.open(self.ORDER_URL)
        form = self._browser.select_form("form#orderForm")
        form["package"] = "1"
        form["payment_gateway"] = "bitpay"
        form["tos"] = True
        page = self._browser.submit_selected()

        return page
