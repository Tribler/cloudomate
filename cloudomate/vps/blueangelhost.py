import re

from bs4 import BeautifulSoup

from cloudomate.gateway import bitpay
from cloudomate.vps.clientarea import ClientArea
from cloudomate.vps.solusvm_hoster import SolusvmHoster
from cloudomate.vps.vpsoption import VpsOption
from cloudomate.wallet import determine_currency


class BlueAngelHost(SolusvmHoster):
    name = "blueangelhost"
    website = "https://www.blueangelhost.com/"
    required_settings = [
        'firstname',
        'lastname',
        'email',
        'address',
        'city',
        'state',
        'zipcode',
        'phonenumber',
        'password',
        'hostname',
        'rootpw',
        'ns1',
        'ns2'
    ]
    clientarea_url = 'https://www.billing.blueangelhost.com/clientarea.php'
    client_data_url = 'https://www.billing.blueangelhost.com/modules/servers/solusvmpro/get_client_data.php'
    gateway = bitpay

    def __init__(self):
        super(BlueAngelHost, self).__init__()

    def register(self, user_settings, vps_option):
        """
        Register RockHoster provider, pay through CoinBase
        :param user_settings: 
        :param vps_option: 
        :return: 
        """
        self.br.open(vps_option.purchase_url)
        self.server_form(user_settings)
        self.br.open('https://www.billing.blueangelhost.com/cart.php?a=view')
        self.br.follow_link(text_regex=r'Checkout')
        self.br.select_form(name='orderfrm')
        self.br.form['customfield[4]'] = ['Google']
        self.user_form(self.br, user_settings, self.gateway.name)
        self.br.select_form(nr=0)
        page = self.br.submit()
        return self.gateway.extract_info(page.geturl())

    def server_form(self, user_settings):
        """
        Fills in the form containing server configuration
        :param user_settings: settings
        :return: 
        """
        self.select_form_id(self.br, 'frmConfigureProduct')
        self.fill_in_server_form(self.br.form, user_settings)
        self.br.form['configoption[72]'] = ['87']  # Ubuntu
        self.br.form['configoption[73]'] = ['91']  # 64 bit
        self.br.submit()

    def start(self):
        blue_page = self.br.open('https://www.blueangelhost.com/openvz-vps/')
        html = blue_page.get_data()
        cookie = self._extract_cookie(html)
        if cookie:
            self.br.set_cookie('PRID=' + self._extract_cookie(html))
        blue_page = self.br.open('https://www.blueangelhost.com/openvz-vps/')
        return self.parse_options(blue_page)

    @staticmethod
    def _extract_cookie(html):
        match = re.search('String\.fromCharCode\((\d+)\)\+String\.fromCharCode\((\d+)\)', html)
        if not match:
            return None
        return ''.join(map(unichr, [int(match.group(1)), int(match.group(2))]))

    def parse_options(self, page):
        soup = BeautifulSoup(page, 'lxml')
        month = soup.find('div', {'id': 'monthly_price'})
        details = month.findAll('div', {'class': 'plan_table'})
        for column in details:
            yield self.parse_blue_options(column)

    @staticmethod
    def parse_blue_options(column):
        price = column.find('div', {'class': 'plan_price_m'}).text.strip()
        currency = determine_currency(price)
        price = price.split('$')[1].split('/')[0]
        planinfo = column.find('ul', {'class': 'plan_info_list'})
        info = planinfo.findAll('li')
        cpu = info[0].text.split(":")[1].strip()
        ram = info[1].text.split(":")[1].strip()
        storage = info[2].text.split(":")[1].strip()
        connection = info[3].text.split(":")[1].strip()
        bandwidth = info[4].text.split("h")[1].strip()

        return VpsOption(
            name=column.find('div', {'class': 'plan_title'}).find('h4').text,
            price=float(price),
            currency=currency,
            cpu=int(cpu.split('C')[0].strip()),
            ram=float(ram.split('G')[0].strip()),
            storage=float(storage.split('G')[0].strip()),
            connection=int(connection.split('G')[0].strip()) * 1000,
            bandwidth=float(bandwidth.split('T')[0].strip()),
            purchase_url=column.find('a')['href']
        )

    def get_status(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        return clientarea.print_services()

    def set_rootpw(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        clientarea.set_rootpw_client_data()

    def get_ip(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        return clientarea.get_client_data_ip(self.client_data_url)

    def info(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        return clientarea.get_client_data_info_dict(self.client_data_url)
