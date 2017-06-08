import sys
from collections import OrderedDict

from bs4 import BeautifulSoup

from cloudomate.gateway import coinbase
from cloudomate.vps.clientarea import ClientArea
from cloudomate.vps.hoster import Hoster
from cloudomate.vps.vpsoption import VpsOption
from cloudomate.wallet import determine_currency


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
    gateway = coinbase

    def __init__(self):
        super(CCIHosting, self).__init__()

    def register(self, user_settings, vps_option):
        """
        Register CCIHosting provider, pay through 
        :param user_settings: 
        :param vps_option: 
        :return: 
        """
        self.br.open(vps_option.purchase_url)
        self.br.select_form(nr=2)
        self.fill_in_server_form(user_settings)
        self.br.submit()
        self.br.open('https://www.ccihosting.com/accounts/cart.php?a=confdomains')
        self.br.follow_link(text_regex="Checkout")
        self.br.select_form(nr=2)
        self.fill_in_user_form(user_settings)
        page = self.br.submit()
        if "checkout" in page.geturl():
            soup = BeautifulSoup(page.get_data(), 'lxml')
            errors = soup.findAll('div', {'class': 'checkout-error-feedback'})
            print(errors[0].text)
            sys.exit(1)
        self.br.select_form(nr=0)
        coinbase_url = self.br.form.attrs.get('action')

        amount, address = self.gateway.extract_info(coinbase_url)

        return amount, address

    def fill_in_server_form(self, user_settings):
        """
        Fills in the form containing server configuration
        :param user_settings: settings
        :return: 
        """
        self.br.form['hostname'] = user_settings.get('hostname')
        self.br.form['rootpw'] = user_settings.get('rootpw')
        self.br.form['ns1prefix'] = user_settings.get('ns1')
        self.br.form['ns2prefix'] = user_settings.get('ns2')
        self.br.form['configoption[214]'] = ['1193']  # Ubuntu
        self.br.form.new_control('text', 'ajax', {'name': 'ajax', 'value': 1})
        self.br.form.new_control('text', 'a', {'name': 'a', 'value': 'confproduct'})
        self.br.form.method = "POST"

    def fill_in_user_form(self, user_settings):
        """
        Fills in the form with user information
        :param user_settings: settings
        :return: 
        """
        self.br.form['firstname'] = user_settings.get('firstname')
        self.br.form['lastname'] = user_settings.get('lastname')
        self.br.form['email'] = user_settings.get('email')
        self.br.form['phonenumber'] = user_settings.get('phonenumber')
        self.br.form['companyname'] = user_settings.get('companyname')
        self.br.form['address1'] = user_settings.get('address')
        self.br.form['city'] = user_settings.get('city')
        self.br.form['country'] = [user_settings.get('countrycode')]
        self.br.form['state'] = user_settings.get('state')
        self.br.form['postcode'] = user_settings.get('zipcode')
        self.br.form['password'] = user_settings.get('password')
        self.br.form['password2'] = user_settings.get('password')
        self.br.form['paymentmethod'] = ['coinbase']
        self.br.find_control('accepttos').items[0].selected = True

    def start(self):
        cci_page = self.br.open('http://www.ccihosting.com/vps.php')
        return self.parse_options(cci_page)

    def parse_options(self, page):
        soup = BeautifulSoup(page, 'lxml')
        tables = soup.findAll('div', {'class': 'box5'})
        for column in tables:
            yield self.parse_cci_options(column)

    @staticmethod
    def parse_cci_options(column):
        price = column.find('div', {'class': 'PriceTag'}).find('span').text.split('U')[0]
        planinfo = column.find('ul')
        info = planinfo.findAll('li')
        return VpsOption(
            name=column.find('div', {'class': 'boxtitle'}).text.split('S')[1].strip(),
            price=float(price.split('$')[1]),
            currency=determine_currency(price),
            cpu=int(info[1].text.split("CPU")[0]),
            ram=float(info[2].text.split("G")[0]),
            storage=float(info[3].text.split("G")[0]),
            bandwidth=float(info[4].text.split("T")[0]),
            connection=int(info[5].text.split("G")[0]) * 1000,
            purchase_url=column.find('a')['href']
        )

    def get_status(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        clientarea.print_services()

    def set_rootpw(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        clientarea.set_rootpw_rootpassword_php()

    def get_ip(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        return clientarea.get_ip()

    def info(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        data = clientarea.get_service_info()
        self._print_info_dict(OrderedDict([
            ('Hostname', data[0]),
            ('IP address', data[1]),
            ('Nameservers', data[2]),
        ]))
