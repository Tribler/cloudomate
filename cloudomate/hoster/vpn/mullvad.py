from __future__ import absolute_import
from __future__ import division
from __future__ import print_function 
from __future__ import unicode_literals

import datetime
import sys
from builtins import round
from builtins import float
from builtins import str
from builtins import int

import requests

from forex_python.converter import CurrencyRates
from future import standard_library

from cloudomate.gateway.custom_mullvad import CustomMullvad
from cloudomate.hoster.vpn.vpn_hoster import VpnHoster, VpnOption, VpnStatus, VpnConfiguration
from cloudomate.util.captchasolver import CaptchaSolver

standard_library.install_aliases()

if sys.version_info > (3, 0):
   from urllib.request import urlretrieve
else:
   from urllib import urlretrieve

class MullVad(VpnHoster):
    REGISTER_URL = "https://www.mullvad.net/en/account/create/"
    LOGIN_URL = "https://www.mullvad.net/en/account/login/"
    ORDER_URL = "https://www.mullvad.net/en/account"
    OPTIONS_URL = "https://www.mullvad.net/en"
    INFO_URL = "https://mullvad.net/en/guides/linux-openvpn-installation/"

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_gateway():
        return CustomMullvad

    @staticmethod
    def get_metadata():
        return "MullVad", "https://www.mnullvad.net/en"

    @staticmethod
    def get_required_settings():
        return {"captcha": ["captchaaccount"]}

    '''
    Action methods of the Hoster that can be called
    '''

    def get_configuration(self):
        return VpnConfiguration('No user name needed',
                                'No password needed', 
                     'Use install_mullvad.py in util folder to install the VPN')

    @classmethod
    def get_options(cls):
        browser = cls._create_browser()
        browser.open(cls.OPTIONS_URL)
        soup = browser.get_current_page()
        p = soup.select("p.hero-description")
        string = p[1].get_text()

        # Calculate the price in USD
        eur = float(string[string.index("€") + 1:string.index("/")])
        price = round(CurrencyRates().convert("EUR","USD", eur), 2)
        
        name, _ = cls.get_metadata()
        option = VpnOption(name, "OpenVPN", price, sys.maxsize, sys.maxsize)
        return [option]

    def get_status(self):
        self._login()

        # Retrieve days left until expiration
        now = datetime.datetime.now(datetime.timezone.utc)
        (online, expiration) = self._check_vpn_date()
        expiration = datetime.timedelta(days=int(expiration))

        # Add the remaining days to the current date to get expiration date
        return VpnStatus(online, now + expiration)

    def purchase(self, wallet, option):
        # Prepare for the purchase on the MullVad website
        if self._settings.get("user", "accountnumber") is None:
            self._register()
        else:
            self._login()
        page = self._order()

        self.pay(wallet, self.get_gateway(), str(page))


    '''
    Hoster-specific methods that are needed to perform the actions
    '''


    def _register(self):
        self._browser.open(self.REGISTER_URL)
        form = self._browser.select_form()
        soup = self._browser.get_current_page()

        # Get captcha needed for registration
        img = soup.select("img.captcha")[0]["src"]
        urlretrieve("https://www.mullvad.net" + img,
                    "captcha.png")
         
        # Solve captcha 
        captcha_solver = CaptchaSolver(self._settings.get("captcha",
                                                          "captchaaccount"))
        solution = captcha_solver.solve_captcha_text_case_sensitive(
                                                                "./captcha.png")
        form["captcha_1"] = solution
        
        self._browser.session.headers["Referer"] = self._browser.get_url()
      
        page = self._browser.submit_selected()

        # Check if registration was successful
        if page.url == self.REGISTER_URL:
            # An error occurred
            print("The captcha was wrong")
            sys.exit(2)

        new_account_number = 0
        
        # Parse page to get new account number
        new_page = str(self._browser.get_current_page())
        for line in new_page.split("\n"):
            if "Your account number:" in line:
                new_account_number = line.split(":")[1]
                new_account_number = new_account_number.split("<")[0].strip(" ")
                break
        self._settings.put("user","accountnumber", new_account_number)
        self._settings.save_settings()

        return page

    def _login(self):
        self._browser.open(self.LOGIN_URL)
        form = self._browser.select_form()
        
        # Use account number to login
        form["account_number"] = self._settings.get("user", "accountnumber")
        self._browser.session.headers["Referer"] = self._browser.get_url()
        page = self._browser.submit_selected()

        # Check if login was successful
        if page.url == self.LOGIN_URL:
            print("The account number is wrong")
            sys.exit(2)

        return page

    def _order(self):
        self._browser.open(self.ORDER_URL)
        form = self._browser.select_form()
        
        # Order one month
        form["months"] = "1"
        self._browser.session.headers["Referer"] = self._browser.get_url()
        self._browser.submit_selected()
        page = self._browser.get_current_page()

        return page

    def _check_vpn_date(self):
        # Checks if VPN expired
        soup = self._browser.get_current_page()
        expire_date = soup.select(".balance-header")[0].get_text()
        expire_date = expire_date.split("\n")[2]
        index_before_date = expire_date.index("in")
        index_after_date = expire_date.index("days")
        expire_date = expire_date[index_before_date + 3:index_after_date - 1]
        
        if (expire_date <= "0"):
            return (False, expire_date)
        else:
            return (True, expire_date)

