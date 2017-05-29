import sys

from bs4 import BeautifulSoup

from cloudomate.vps.hoster import Hoster
from cloudomate.vps.vpsoption import VpsOption


class CCIHosting(Hoster):
    name = "ccihosting"
    website = "http://www.ccihosting.com/"
    clientarea_url = "https://www.ccihosting.com/accounts/clientarea.php"
    required_settings = [
        'firstname',
        'lastname',
        'email',
        'phonenumber',
        'address',
        'city',
        'countrycode',
        'state',
        'zipcode',
        'password',
        'hostname',
        'rootpw'
    ]

    def purchase(self, user_settings, vps_option):
        """
        Purchase a CCIHosting VPS.
        :param user_settings: settings
        :param vps_option: server configuration
        :return: 
        """
        print("Purchase")
        # # self.browser.set_debug_http(True)
        # # self.browser.set_debug_responses(True)
        # # self.browser.set_debug_redirects(True)
        self.register(user_settings, vps_option)
        pass

    def register(self, user_settings, vps_option):
        """
        Register CCIHosting provider, pay through 
        :param user_settings: 
        :param vps_option: 
        :return: 
        """
        self.browser.open(vps_option.purchase_url)
        self.browser.select_form(nr=2)
        self.fill_in_server_form(user_settings)
        self.browser.submit()
        self.browser.open('https://www.ccihosting.com/accounts/cart.php?a=confdomains')
        self.browser.follow_link(text_regex="Checkout")
        self.browser.select_form(nr=2)
        self.fill_in_user_form(user_settings)
        page = self.browser.submit()
        if "checkout" in page.geturl():
            soup = BeautifulSoup(page.get_data(), 'lxml')
            errors = soup.findAll('div', {'class': 'checkout-error-feedback'})
            print(errors[0].text)
            sys.exit(1)
        self.browser.select_form(nr=0)
        coinbase_url = self.browser.form.attrs.get('action')

        print("Coinbase URL:", coinbase_url)

    def fill_in_server_form(self, user_settings):
        """
        Fills in the form containing server configuration
        :param user_settings: settings
        :return: 
        """
        self.browser.form['hostname'] = user_settings.get('hostname')
        self.browser.form['rootpw'] = user_settings.get('rootpw')
        self.browser.form['ns1prefix'] = user_settings.get('ns1')
        self.browser.form['ns2prefix'] = user_settings.get('ns2')
        self.browser.form['configoption[214]'] = ['1193']  # Ubuntu
        self.browser.form.new_control('text', 'ajax', {'name': 'ajax', 'value': 1})
        self.browser.form.new_control('text', 'a', {'name': 'a', 'value': 'confproduct'})
        self.browser.form.method = "POST"

    def fill_in_user_form(self, user_settings):
        """
        Fills in the form with user information
        :param user_settings: settings
        :return: 
        """
        self.browser.form['firstname'] = user_settings.get('firstname')
        self.browser.form['lastname'] = user_settings.get('lastname')
        self.browser.form['email'] = user_settings.get('email')
        self.browser.form['phonenumber'] = user_settings.get('phonenumber')
        self.browser.form['companyname'] = user_settings.get('companyname')
        self.browser.form['address1'] = user_settings.get('address')
        self.browser.form['city'] = user_settings.get('city')
        self.browser.form['country'] = [user_settings.get('countrycode')]
        self.browser.form['state'] = user_settings.get('state')
        self.browser.form['postcode'] = user_settings.get('zipcode')
        self.browser.form['password'] = user_settings.get('password')
        self.browser.form['password2'] = user_settings.get('password')
        self.browser.form['paymentmethod'] = ['coinbase']
        self.browser.find_control('accepttos').items[0].selected = True

    def options(self):
        options = self.start()
        self.configurations = list(options)
        return self.configurations

    def __init__(self):
        pass

    def start(self):
        self.browser = self._create_browser()
        cci_page = self.browser.open('http://www.ccihosting.com/vps.php')
        return self.parse_options(cci_page)

    def parse_options(self, page):
        soup = BeautifulSoup(page, 'lxml')
        tables = soup.findAll('div', {'class': 'box5'})
        for column in tables:
            yield self.parse_cci_options(column)

    @staticmethod
    def parse_cci_options(column):
        option = VpsOption()
        option.name = column.find('div', {'class': 'boxtitle'}).text.split('S')[1].strip()
        option.price = column.find('div', {'class': 'PriceTag'}).find('span').text.split('U')[0]
        option.price = option.price.split('$')[1]
        planinfo = column.find('ul')
        info = planinfo.findAll('li')
        option.cpu = info[1].text.split("CPU")[0] + info[1].text.split("CPU")[1]
        option.ram = info[2].text.split("R")[0]
        option.storage = info[3].text.split("S")[0]
        option.bandwidth = info[4].text.split("Ba")[0]
        option.connection = info[5].text.split("/")[0]
        option.purchase_url = column.find('a')['href']
        return option

    def get_status(self, user_settings):
        self._clientarea_get_status(user_settings, self.clientarea_url)

    def set_rootpw(self, user_settings):
        self._clientarea_set_rootpw(user_settings, self.clientarea_url)

    def get_ip(self, user_settings):
        self._clientarea_get_ip(user_settings, self.clientarea_url, self.client_data_url)
