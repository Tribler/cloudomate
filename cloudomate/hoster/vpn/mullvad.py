from __future__ import absolute_import
from __future__ import division
from __future__ import print_function 
from __future__ import unicode_literals

import datetime
import os
import shutil
import sys
import zipfile
from builtins import round
from builtins import float
from builtins import str

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
    CONFIGURATION_URL = "https://mullvad.net/en/download/config/"

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
        return {"anticaptcha": ["accountkey"]}

    '''
    Action methods of the Hoster that can be called
    '''

    def get_configuration(self):
        self._download_files()

        userpass_file = open("./config-files/mullvad_userpass.txt", "r")
        username = userpass_file.readline().strip()
        password = userpass_file.readline().strip()

        conf_file = open("./config-files/mullvad_se-sto.conf", "r")
        conf = conf_file.read()

        ca_file = open("./config-files/mullvad_ca.crt", "r")
        ca = ca_file.read()

        # include the certificate
        conf = conf.replace("ca mullvad_ca.crt", "<ca>\n" + ca + "</ca>")

        # remove userpass as it is added by cmdline.py
        conf = conf.replace("auth-user-pass mullvad_userpass.txt", "")

        return VpnConfiguration(username, password, conf)

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
        expire_date = self._get_expiration_date()
        expire_date = datetime.datetime.strptime(expire_date, "%d %B %Y")

        online = (expire_date > self._get_current_date())

        return VpnStatus(online, expire_date)

    def purchase(self, wallet, option):
        # Prepare for the purchase on the MullVad website
        if self._settings.has_key("user", "accountnumber"):
            self._login()
        else:
            self._register()
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
        captcha_solver = CaptchaSolver(self._settings.get("anticaptcha",
                                                          "accountkey"))
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
        form = self._browser.select_form('form[action="/en/account/bitcoin/"]')

        # Order one month
        form["months"] = "1"
        self._browser.session.headers["Referer"] = self._browser.get_url()
        self._browser.submit_selected()
        page = self._browser.get_current_page()

        return page

    def _get_expiration_date(self):
        # Checks if VPN expired
        soup = self._browser.get_current_page()
        expire_date = soup.select(".balance-header")[0].get_text()
        expire_date = expire_date.split("\n")[2].strip()
        return expire_date

    @staticmethod
    def _get_current_date():
        return datetime.datetime.now()

    # Download configuration files for setting up VPN and extract them
    def _download_files(self):
        # Fill information on website to get right files for openVPN
        self._browser.open(self.CONFIGURATION_URL)
        form = self._browser.select_form()
        form["account_token"] = self._settings.get("user", "accountnumber")
        form["platform"] = "linux"
        form["region"] = "se-sto"
        form["port"] = "0"
        self._browser.session.headers["Referer"] = self._browser.get_url()
        response = self._browser.submit_selected()
        content = response.content

        # Create the folder that will store the configuration files
        result = os.popen("mkdir -p config-files").read()
        print(result)

        # Download the zip file to the right location
        files_path = "./config-files/config.zip"
        with open(files_path, "wb") as output:
            output.write(content)

        # Unzip files
        zip_file = zipfile.ZipFile(files_path, "r")
        for member in zip_file.namelist():
            filename = os.path.basename(member)
            # Skip directories
            if not filename:
                continue

            # Copy file (taken from zipfile's extract)
            source = zip_file.open(member)
            target = open(os.path.join("./config-files/", filename), "wb")
            with source, target:
                shutil.copyfileobj(source, target)

        # Delete zip file
        os.remove(files_path)
