import itertools

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
        Register BlueAngelHost provider, pay through CoinBase
        :param user_settings: 
        :param vps_option: 
        :return: 
        """
        self.br.open(vps_option.purchase_url)
        self.server_form(user_settings)
        self.br.open('https://www.billing.blueangelhost.com/cart.php?a=view')

        summary = self.br.get_current_page().find('div', class_='summary-container')
        self.br.follow_link(summary.find('a', class_='btn-checkout'))

        self.br.select_form(selector='form[name=orderfrm]')
        self.br.get_current_form()['customfield[4]'] = 'Google'
        self.user_form(self.br, user_settings, self.gateway.name)

        self.br.select_form(nr=0)
        self.br.submit_selected()
        return self.gateway.extract_info(self.br.get_url())

    def server_form(self, user_settings):
        """
        Fills in the form containing server configuration
        :param user_settings: settings
        :return: 
        """
        form = self.br.select_form('form#frmConfigureProduct')
        self.fill_in_server_form(form, user_settings)
        form['configoption[72]'] = '87'  # Ubuntu
        form['configoption[73]'] = '91'  # 64 bit
        self.br.submit_selected()

    def start(self):
        self.br.open("https://www.blueangelhost.com/openvz-vps/")
        options = self.parse_options(self.br.get_current_page())

        self.br.open("https://www.blueangelhost.com/kvm-vps/")
        options = itertools.chain(options, self.parse_options(self.br.get_current_page(), is_kvm=True))

        return options

    def parse_options(self, page, is_kvm=False):
        month = page.find('div', {'id': 'monthly_price'})
        details = month.findAll('div', {'class': 'plan_table'})
        for column in details:
            yield self.parse_blue_options(column, is_kvm=is_kvm)

    @staticmethod
    def parse_blue_options(column, is_kvm=False):
        if is_kvm:
            split_char = ' '
        else:
            split_char = ':'

        price = column.find('div', {'class': 'plan_price_m'}).text.strip()
        currency = determine_currency(price)
        price = price.split('$')[1].split('/')[0]
        planinfo = column.find('ul', {'class': 'plan_info_list'})
        info = planinfo.findAll('li')
        cpu = info[0].text.split(split_char)[1].strip()
        ram = info[1].text.split(split_char)[1].strip()
        storage = info[2].text.split(split_char)[1].strip()
        connection = info[3].text.split(split_char)[1].strip()
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
