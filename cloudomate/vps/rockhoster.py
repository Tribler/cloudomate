import itertools

from bs4 import BeautifulSoup
from mechanize._form_controls import ControlNotFoundError

from cloudomate.gateway import coinbase
from cloudomate.vps.clientarea import ClientArea
from cloudomate.vps.solusvm_hoster import SolusvmHoster
from cloudomate.vps.vpsoption import VpsOption
from cloudomate.wallet import determine_currency


class RockHoster(SolusvmHoster):
    name = "rockhoster"
    website = "https://rockhoster.com/"
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
        'rootpw']
    clientarea_url = 'https://rockhoster.com/cloud/clientarea.php'
    client_data_url = 'https://rockhoster.com/cloud/modules/servers/solusvmpro/get_client_data.php'
    gateway = coinbase

    def __init__(self):
        super(RockHoster, self).__init__()

    def register(self, user_settings, vps_option):
        """
        Register RockHoster provider, pay through CoinBase
        :param user_settings: 
        :param vps_option: 
        :return: 
        """
        self.br.open(vps_option.purchase_url)
        self.server_form(user_settings)
        self.br.open('https://rockhoster.com/cloud/cart.php?a=view')
        self.br.follow_link(text_regex=r'Checkout')
        self.br.select_form(nr=4)
        self.user_form(self.br, user_settings, self.gateway.name)
        page = self.br.follow_link(url_regex="coinbase")
        return self.gateway.extract_info(page.geturl())

    def server_form(self, user_settings):
        """
        Fills in the form containing server configuration.
        :param user_settings: settings
        :return: 
        """
        self.select_form_id(self.br, 'frmConfigureProduct')
        self.fill_in_server_form(self.br.form, user_settings, nameservers=False)
        try:
            self.br.form['configoption[20]'] = ['53']  # Paris
            self.br.form['configoption[2]'] = ['13']
        except ControlNotFoundError:
            self.br.form['configoption[19]'] = ['51']  # Paris
            self.br.form['configoption[16]'] = ['41']  # Ubuntu 14.04
        self.br.submit()

    def start(self):
        """
        Linux (OpenVZ) and Windows (KVM) pages are slightly different, therefore their pages are parsed by different 
        methoods. Windows configurations allow a selection of Linux distributions, but not vice-versa.
        :return: possible configurations.
        """
        openvz_hosting_page = self.br.open("https://rockhoster.com/linux.html")
        options = self.parse_openvz_hosting(openvz_hosting_page.get_data())

        kvm_hosting_page = self.br.open("https://rockhoster.com/windows-vps")
        options = itertools.chain(options, self.parse_kvm_hosting(kvm_hosting_page.get_data()))
        return options

    def parse_openvz_hosting(self, page):
        soup = BeautifulSoup(page, "lxml")
        details = soup.findAll('div', {'class': 'pacdetails'})
        for column in details:
            yield self.parse_openvz_option(column)

    @staticmethod
    def parse_openvz_option(column):
        elements = column.findAll("li")
        price = column.div.strong.text
        currency = determine_currency(price)
        price = price.split('$')[1].split('/')[0]
        storage = elements[0].text.split(": ")[1]
        ram = elements[1].text.split("G")[0]
        connection = elements[5].text.split(": ")[1]

        return VpsOption(
            name=column.div.h2.string,
            price=float(price),
            currency=currency,
            storage=float(storage.split("G")[0]),
            ram=float(ram.split("RAM: ")[1]),
            bandwidth='unmetered',
            cpu=int(elements[3].text.split(':')[1]),
            connection=int(connection.split('M')[0]),
            purchase_url=column.find('div', {'class': 'bottom'}).a['href']
        )

    def parse_kvm_hosting(self, page):
        soup = BeautifulSoup(page, "lxml")
        details = soup.findAll('div', {'class': 'pacdetails'})
        for column in details:
            yield self.parse_kvm_option(column)

    @staticmethod
    def parse_kvm_option(column):
        elements = column.findAll("li")
        price = column.div.strong.text
        currency = determine_currency(price)
        price = price.split('$')[1].split('/')[0]
        ram = elements[1].text.split("RAM:")[1].strip()
        storage = elements[0].text.split(": ")[1]

        return VpsOption(
            name=column.div.h2.string,
            price=float(price),
            currency=currency,
            connection=1000,
            cpu=int(elements[3].text.split(':')[1]),
            ram=int(ram.split('M')[0]) / 1024,
            bandwidth='unmetered',
            storage=float(storage.split('G')[0]),
            purchase_url=column.find('div', {'class': 'bottom'}).a['href']
        )

    def get_status(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        return clientarea.print_services()

    def set_rootpw(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        return clientarea.set_rootpw_client_data()

    def get_ip(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        return clientarea.get_client_data_ip(self.client_data_url)

    def info(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        return clientarea.get_client_data_info_dict(self.client_data_url)
