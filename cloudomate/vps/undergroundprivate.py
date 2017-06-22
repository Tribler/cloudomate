import sys
from bs4 import BeautifulSoup

from cloudomate.gateway import coinbase
from cloudomate.vps.clientarea import ClientArea
from cloudomate.vps.solusvm_hoster import SolusvmHoster
from cloudomate.vps.vpsoption import VpsOption
from cloudomate.wallet import determine_currency


class UndergroundPrivate(SolusvmHoster):
    name = "underground"
    website = "https://undergroundprivate.com"
    clientarea_url = "https://www.clientlogin.sx/clientarea.php"
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
        super(UndergroundPrivate, self).__init__()

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

    def register(self, user_settings, vps_option):
        page = self.br.open(vps_option.purchase_url)
        if 'add' in page.geturl():
            print 'Out of Stock'
            sys.exit(2)
        self.server_form(user_settings)
        self.br.open('https://www.clientlogin.sx/cart.php?a=view')
        self.br.form = list(self.br.forms())[2]
        promobutton = self.br.form.find_control(name="validatepromo")
        promobutton.disabled = True
        self.user_form(self.br, user_settings, 'blockchainv2', errorbox_class='errorbox', acceptos=False)
        html = self.br.response()
        btcsoup = BeautifulSoup(html, 'lxml')
        url = btcsoup.find('iframe')['src']
        page = self.br.open(url)
        soup = BeautifulSoup(page.get_data(), 'lxml')
        info = soup.findAll('input')
        amount = info[0]['value']
        address = info[1]['value']
        return amount, address

    def server_form(self, user_settings):
        """
        Fills in the form containing server configuration
        :param user_settings: settings
        :return: 
        """
        self.br.form = list(self.br.forms())[1]
        self.fill_in_server_form(self.br.form, user_settings)
        self.br.form['configoption[7]'] = ['866']  # Ubuntu
        self.br.submit()

    def start(self):
        russia_page = self.br.open('https://undergroundprivate.com/russiaoffshorevps.html')
        options = list(self.parse_r_options(russia_page))
        # france_page = self.br.open('https://undergroundprivate.com/franceoffshore.html')
        # options = itertools.chain(options, self.parse_f_options(france_page))
        return options

    @staticmethod
    def parse_france_options(info):
        return VpsOption(
            name=info[0].text.strip(),
            price=float(info[1].find('span').text.split('$')[1]),
            currency=determine_currency(info[1].find('span').text),
            cpu=int(info[2].contents[2].split('cores')[0]),
            ram=float(info[4].text.split("G")[0]),
            storage=float(info[3].text.split("G")[0]),
            bandwidth='unmetered',
            connection=int(info[6].text.split("G")[0]) * 1000,
            purchase_url=info[11].find('a')['href']
        )

    def parse_f_options(self, page):
        soup = BeautifulSoup(page, 'lxml')
        tables = soup.findAll('div', {'class': 'small-12 large-4 medium-4 columns '})
        for table in tables[:5]:
            info = table.findAll('li')
            if info[1].find('span').text.split('$')[1] != '-':
                yield self.parse_france_options(info)

    def parse_r_options(self, page):
        soup = BeautifulSoup(page, 'lxml')
        tables = soup.findAll('div', {'class': 'small-12 large-4 medium-4 columns '})
        for table in tables[:5]:
            info = table.findAll('li')
            if info[1].find('span').text.split('$')[1] != '-':
                yield self.parse_russia_options(info)

    @staticmethod
    def parse_russia_options(info):
        return VpsOption(
            name=info[0].text.strip(),
            price=float(info[1].find('span').text.split('$')[1]),
            currency=determine_currency(info[1].find('span').text),
            cpu=int(info[2].contents[2].split('cores')[0]),
            ram=float(info[4].text.split("G")[0]),
            storage=float(info[3].text.split("G")[0]),
            bandwidth='unmetered',
            connection=int(info[6].text.split("G")[0]) * 1000,
            purchase_url=info[13].find('a')['href']
        )
