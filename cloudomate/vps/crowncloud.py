import mechanize
import sys
from bs4 import BeautifulSoup

from cloudomate.gateway import bitpay
from cloudomate.vps.hoster import Hoster
from cloudomate.vps.vpsoption import VpsOption
import cloudomate.gateway.bitpay


class CrownCloud(Hoster):
    name = "crowncloud"
    website = "http://crowncloud.net/"
    required_settings = ["rootpw"]
    br = None

    def __init__(self):
        self.br = self._create_browser()
        # self.br.set_debug_redirects(True)
        # self.br.set_debug_http(True)
        # self.br.set_debug_responses(True)
        pass

    def purchase(self, user_settings, vps_option):
        """
        Purchase a CrownCloud VPS.
        :param user_settings: settings
        :param vps_option: server configuration
        :return: 
        """
        print("Purchase")
        self.register(user_settings, vps_option)
        pass

    def register(self, user_settings, vps_option):
        """
        Register CrownCloud provider, pay through BitPay
        :param user_settings: 
        :param vps_option: 
        :return: 
        """
        self.br.open("https://crowncloud.net")
        self.br.open(vps_option.purchase_url)
        self.br.select_form(nr=2)
        self.fill_in_server_form(user_settings)
        self.br.submit()
        self.br.open('https://crowncloud.net/clients/cart.php?a=view')
        self.br.select_form(nr=2)
        self.fill_in_user_form(user_settings)
        promobutton = self.br.form.find_control(type="submitbutton", nr=0)
        promobutton.disabled = True
        page = self.br.submit()
        if "checkout" in page.geturl():
            soup = BeautifulSoup(page.get_data(), 'lxml')
            errors = soup.findAll('div', {'class': 'errorbox'})
            print(errors[0].text)
            sys.exit(1)
        self.br.select_form(nr=0)
        page = self.br.submit()
        (amount, address) = cloudomate.gateway.bitpay.extract_info(page.geturl())
        print("Pay", amount, "to", address)

    def fill_in_server_form(self, user_settings):
        """
        Fills in the form containing server configuration.
        :param user_settings: settings
        :return: 
        """
        # self.br.form['hostname'] = user_settings.get("hostname")
        # self.br.form['rootpw'] = user_settings.get("rootpw")
        # self.br.form['ns1prefix'] = user_settings.get("ns1")
        # self.br.form['ns2prefix'] = user_settings.get("ns2")
        self.br.form['configoption[1]'] = ['56']
        self.br.form['configoption[8]'] = ['52']
        self.br.form['configoption[9]'] = '0'
        self.br.form.new_control('text', 'ajax', {'name': 'ajax', 'value': 1})
        self.br.form.new_control('text', 'a', {'name': 'a', 'value': 'confproduct'})
        self.br.form.method = "POST"

    def fill_in_user_form(self, user_settings):
        """
        Fills in the form with user information.
        :param user_settings: settings
        :return: 
        """
        self.br.form['firstname'] = user_settings.get("firstname")
        self.br.form['lastname'] = user_settings.get("lastname")
        self.br.form['email'] = user_settings.get("email")
        self.br.form['phonenumber'] = user_settings.get("phonenumber")
        self.br.form['companyname'] = user_settings.get("companyname")
        self.br.form['address1'] = user_settings.get("address")
        self.br.form['city'] = user_settings.get("city")
        countrycode = user_settings.get("countrycode")

        # State input changes based on country: USA (default) -> Select, Other -> Text
        self.br.form['state'] = user_settings.get("state")
        self.br.form['postcode'] = user_settings.get("zipcode")
        self.br.form['country'] = [countrycode]
        self.br.form['password'] = user_settings.get("password")
        self.br.form['password2'] = user_settings.get("password")
        self.br.form['paymentmethod'] = ['bitpay']
        self.br.find_control('accepttos').items[0].selected = True

    def options(self):
        options = self.start()
        self.configurations = list(options)
        return self.configurations

    def start(self):
        browser = mechanize.Browser()
        browser.set_handle_robots(False)
        browser.addheaders = [('User-agent', 'Firefox')]

        clown_page = browser.open('http://crowncloud.net/openvz.php')
        return self.parse_options(clown_page)

    def parse_options(self, page):
        soup = BeautifulSoup(page, 'lxml')
        tables = soup.findAll('table')
        for details in tables:
            for column in details.findAll('tr'):
                if len(column.findAll('td')) > 0:
                    yield self.parse_clown_options(column)

    @staticmethod
    def parse_clown_options(column):
        elements = column.findAll('td')
        option = VpsOption()
        option.name = elements[0].text
        option.ram = elements[1].text.split('/')[0]
        option.storage = elements[2].text
        option.cpu = elements[3].text
        option.bandwidth = elements[4].text
        option.connection = elements[7].text
        option.price = elements[8].text
        option.purchase_url = elements[9].find('a')['href']
        return option


if __name__ == "__main__":
    CrownCloud.start()
