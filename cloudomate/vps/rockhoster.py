import itertools

from bs4 import BeautifulSoup

from cloudomate.gateway import coinbase
from cloudomate.vps.clientarea import ClientArea
from cloudomate.vps.hoster import Hoster
from cloudomate.vps.vpsoption import VpsOption
from cloudomate.wallet import determine_currency


class RockHoster(Hoster):
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
        self.br.select_form(nr=4)
        self.fill_in_server_form(user_settings)
        self.br.submit()
        self.br.open('https://rockhoster.com/cloud/cart.php?a=view')
        self.br.follow_link(text_regex=r"Checkout")
        self.br.select_form(nr=4)
        self.fill_in_user_form(user_settings)
        self.br.submit()
        page = self.br.follow_link(url_regex="coinbase")
        amount, address = self.gateway.extract_info(page.geturl())
        return amount, address

    def fill_in_server_form(self, user_settings):
        """
        Fills in the form containing server configuration.
        :param user_settings: settings
        :return: 
        """
        self.br.form['hostname'] = user_settings.get("hostname")
        self.br.form['rootpw'] = user_settings.get("rootpw")
        self.br.form['ns1prefix'] = user_settings.get("ns1")
        self.br.form['ns2prefix'] = user_settings.get("ns2")
        self.br.form['configoption[20]'] = ['53']  # Paris
        self.br.form['configoption[2]'] = ['13']
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
        self.br.form['paymentmethod'] = ['coinbase']
        self.br.find_control('accepttos').items[0].selected = True

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
        clientarea.print_services()

    def set_rootpw(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        clientarea.set_rootpw_client_data()

    def get_ip(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        return clientarea.get_client_data_ip(self.client_data_url)

    def info(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        info_dict = clientarea.get_client_data_info_dict(self.client_data_url)
        self._print_info_dict(info_dict)
