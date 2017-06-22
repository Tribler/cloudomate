from collections import OrderedDict

from bs4 import BeautifulSoup

from cloudomate.gateway import coinbase
from cloudomate.vps.clientarea import ClientArea
from cloudomate.vps.solusvm_hoster import SolusvmHoster
from cloudomate.vps.vpsoption import VpsOption
from cloudomate.wallet import determine_currency


class Pulseservers(SolusvmHoster):
    """
    PulseServers contains the logic to view hosting configurations and to 
    purchase servers at Pulseservers.
    """
    name = "pulseservers"
    website = "https://pulseservers.com/"
    required_settings = [
        'firstname',
        'lastname',
        'email',
        'phonenumber',
        'address',
        'city',
        'state',
        'zipcode',
        'password',
        'hostname',
        'rootpw'
    ]
    clientarea_url = 'https://www.pulseservers.com/billing/clientarea.php'
    gateway = coinbase

    def __init__(self):
        super(Pulseservers, self).__init__()

    def start(self):
        """
        Open browser to hoster website and return parsed options
        :return: parsed options
        """
        response = self.br.open('https://pulseservers.com/vps-linux.html')
        return self.parse_options(response)

    def parse_options(self, response):
        """
        Parse options of hosting configurations
        :param response: Site to be parsed
        :return: list of configurations
        """
        site = BeautifulSoup(response.read(), 'lxml')
        pricingboxes = site.findAll('div', {'class': 'pricing-box'})
        self.configurations = [self._parse_box(box) for box in pricingboxes]
        return self.configurations

    @staticmethod
    def _parse_box(box):
        """
        Parse a single hosting configuration
        :param box: Div containing hosting details
        :return: VpsOption containing hosting details
        """
        details = box.findAll('li')
        storage = details[4].strong.text
        if storage == '1TB':
            storage = 1024.0
        else:
            storage = float(storage.split('G')[0])

        connection = details[5].strong.text.split('G')[0]
        connection = int(connection) * 1000
        return VpsOption(
            name=details[0].h4.text,
            price=float(details[1].h1.text.split('$')[1]),
            currency=determine_currency(details[1].h1.text),
            cpu=int(details[2].strong.text.split('C')[0]),
            ram=float(details[3].strong.text.split('G')[0]),
            storage=storage,
            connection=connection,
            bandwidth='unmetered',
            purchase_url=details[9].a['href']
        )

    @staticmethod
    def _beautify_cpu(cores, speed):
        """
        Format cores and speed to fit cpu column
        :param cores: cores text
        :param speed: speed text
        :return: formatted string
        """
        spl = cores.split()
        return '{0}c/{1}t {2}'.format(spl[0], spl[3], speed[:-4])

    def register(self, user_settings, vps_option):
        """
        Register at Pulseservers provider and pay through coinbase
        :param user_settings: 
        :param vps_option: 
        :return: 
        """
        self.br.open(vps_option.purchase_url)
        self.server_form(user_settings)
        self.br.open('https://www.pulseservers.com/billing/cart.php?a=confdomains')
        self.select_form_id(self.br, 'mainfrm')
        promobutton = self.br.form.find_control(name="validatepromo")
        promobutton.disabled = True
        self.user_form(self.br, user_settings, self.gateway.name, errorbox_class='errorbox')
        self.br.select_form(nr=0)
        page = self.br.submit()
        return self.gateway.extract_info(page.geturl())

    def server_form(self, user_settings):
        """
        Fill in the form with user information
        :param user_settings: settings
        :return: 
        """
        self.select_form_id(self.br, 'orderfrm')
        self.fill_in_server_form(self.br.form, user_settings, nameservers=False)
        self.br.form['billingcycle'] = ['monthly']
        self.br.submit()

    def get_status(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        return clientarea.print_services()

    def set_rootpw(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        clientarea.set_rootpw_rootpassword_php()

    def get_ip(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        return clientarea.get_ip()

    def info(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        data = clientarea.get_service_info()
        return OrderedDict([
            ('Hostname', data[0]),
            ('IP address', data[1]),
            ('Nameserver 1', data[2].split('.com')[0] + '.com'),
            ('Nameserver 2', data[2].split('.com')[1]),
        ])
