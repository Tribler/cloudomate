from collections import OrderedDict

from cloudomate.gateway import coinbase
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.clientarea import ClientArea
from cloudomate.hoster.vps.vpsoption import VpsOption
from cloudomate.wallet import determine_currency


class CCIHosting(SolusvmHoster):
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
        self._browser.open(vps_option.purchase_url)
        self.server_form(user_settings)  # Add item to cart
        self._browser.open('https://www.ccihosting.com/accounts/cart.php?a=confdomains')

        summary = self._browser.get_current_page().find('div', class_='summary-container')
        self._browser.follow_link(summary.find('a', class_='btn-checkout'))

        self._browser.select_form(selector='form[name=orderfrm]')
        self.user_form(self._browser, user_settings, self.gateway.name)

        coinbase_url = self._browser.get_current_page().find('form')['action']
        return self.gateway.extract_info(coinbase_url)

    def server_form(self, user_settings):
        """
        Using a form does for some reason not work, so use post request
        :param user_settings: settings
        :return: 
        """
        self._browser.post('https://www.ccihosting.com/accounts/cart.php', {
            'ajax': '1',
            'a': 'confproduct',
            'configure': 'true',
            'i': '0',
            'billingcycle': 'monthly',
            'hostname': user_settings.get('hostname'),
            'rootpw': user_settings.get('rootpw'),
            'ns1prefix': user_settings.get('ns1'),
            'ns2prefix': user_settings.get('ns2'),
            'configoption[214]': '1193',  # Ubuntu 16.04
            'configoption[258]': '955',
        })

    def start(self):
        self._browser.open('https://www.ccihosting.com/offshore-vps.html')
        return self.parse_options(self._browser.get_current_page())

    def parse_options(self, page):
        tables = page.findAll('div', class_='p_table')
        for column in tables:
            yield self.parse_cci_options(column)

    @staticmethod
    def parse_cci_options(column):
        header = column.find('div', class_='phead')
        price = column.find('span', class_='starting-price')
        info = column.find('ul').findAll('li')
        return VpsOption(
            name=header.find('h2').contents[0],
            price=float(price.contents[0]),
            currency=determine_currency(price.previous_sibling.strip()),
            cpu=int(info[1].find('strong').contents[0]),
            ram=float(info[2].find('strong').contents[0]),
            storage=float(info[3].find('strong').contents[0]),
            bandwidth=info[4].find('strong').contents[0].lower(),
            connection=10,
            purchase_url=column.find('a')['href']
        )

    def get_status(self, user_settings):
        clientarea = ClientArea(self._browser, self.clientarea_url, user_settings)
        return clientarea.print_services()

    def set_rootpw(self, user_settings):
        clientarea = ClientArea(self._browser, self.clientarea_url, user_settings)
        clientarea.set_rootpw_rootpassword_php()

    def get_ip(self, user_settings):
        clientarea = ClientArea(self._browser, self.clientarea_url, user_settings)
        return clientarea.get_ip()

    def info(self, user_settings):
        clientarea = ClientArea(self._browser, self.clientarea_url, user_settings)
        data = clientarea.get_service_info()
        return OrderedDict([
            ('Hostname', data[0]),
            ('IP address', data[1]),
            ('Nameservers', data[2]),
        ])
