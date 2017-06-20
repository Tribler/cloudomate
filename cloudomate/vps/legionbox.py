import itertools
from collections import OrderedDict

from bs4 import BeautifulSoup

from cloudomate.gateway import coinbase
from cloudomate.vps.clientarea import ClientArea
from cloudomate.vps.solusvm_hoster import SolusvmHoster
from cloudomate.vps.vpsoption import VpsOption


class LegionBox(SolusvmHoster):
    name = "legionbox"
    website = "https://legionbox.com/"
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

    clientarea_url = 'https://legionbox.com/billing/clientarea.php'
    gateway = coinbase

    def __init__(self):
        super(LegionBox, self).__init__()

    def start(self):
        hosting_page = self.br.open("https://legionbox.com/virtual-servers/")
        soup = BeautifulSoup(hosting_page.get_data(), 'lxml')
        options = self.parse_options(soup.find('div', {'id': 'Linux'}).ul)
        options = itertools.chain(options, self.parse_options(soup.find('div', {'id': 'SSD-VPS'}).ul))
        return options

    def parse_options(self, options_list):
        items = options_list.findAll('li')
        for item in items:
            yield self.parse_option(item)

    @staticmethod
    def parse_option(item):
        divs = item.findAll('div')
        return VpsOption(
            name=item.h4.text,
            price=float(item.strong.text[1:]),
            currency='USD',
            connection=1000,
            cpu=divs[2].strong.text[0],
            ram=divs[3].strong.text.split(' ')[0],
            bandwidth='unmetered',
            storage=divs[4].strong.text.split(' ')[0],
            purchase_url=item.a['href']
        )

    def get_status(self, user_settings):
        clientarea = LegionBoxClientArea(self.br, self.clientarea_url, user_settings)
        clientarea.print_services()

    def set_rootpw(self, user_settings):
        clientarea = LegionBoxClientArea(self.br, self.clientarea_url, user_settings)
        clientarea.set_rootpw_rootpassword_php()

    def get_ip(self, user_settings):
        clientarea = LegionBoxClientArea(self.br, self.clientarea_url, user_settings)
        return clientarea.get_service_info()[2]

    def info(self, user_settings):
        clientarea = LegionBoxClientArea(self.br, self.clientarea_url, user_settings)
        data = clientarea.get_service_info()
        return OrderedDict([
            ('Name', data[1]),
            ('Date due', data[0]),
            ('IP address', data[2]),
        ])

    def register(self, user_settings, vps_option):
        """
        Register LegionBox provider, pay through CoinBase
        :param user_settings: 
        :param vps_option: 
        :return: 
        """
        self.br.open(vps_option.purchase_url)
        self.server_form(user_settings)
        self.br.open('https://legionbox.com/billing/cart.php?a=view')
        self.select_form_id(self.br, 'mainfrm')
        promobutton = self.br.form.find_control(type="submit", nr=0)
        promobutton.disabled = True
        self.user_form(self.br, user_settings, self.gateway.name, errorbox_class='errorbox')
        page = self.br.follow_link(url_regex="coinbase")
        return self.gateway.extract_info(page.geturl())
        # page = self.br.follow_link(url_regex="coinbase")
        # return self.gateway.extract_info(page.geturl())

    def server_form(self, user_settings):
        """
        Fills in the form containing server configuration.
        :param user_settings: settings
        :return: 
        """
        self.select_form_id(self.br, 'orderfrm')
        self.fill_in_server_form(self.br.form, user_settings, nameservers=False)
        self.br.form['configoption[10]'] = ['39']  # Russia
        self.br.form['configoption[11]'] = ['49']  # Ubuntu 14.10
        self.br.form.action = 'https://legionbox.com/billing/cart.php'
        self.br.submit()


class LegionBoxClientArea(ClientArea):
    """
    Custom ClientArea methods are used because LegionBox uses a presumably older version of SolusVM than other
    providers.
    """

    def _extract_services(self, html):
        soup = BeautifulSoup(html, 'lxml')
        rows = soup.find('table', {'class': 'table'}).tbody.findAll('tr')
        self.services = []
        for row in rows:
            tds = row.findAll('td', recursive=False)
            status = tds[4].span['class'][-1]

            self.services.append({
                'id': tds[5].div.a['href'].split('id=')[1],
                'product': tds[0].strong.text.split(' - ')[1],
                'price': tds[1].text,
                'term': tds[2].text,
                'next_due_date': tds[3].text,
                'status': status,
                'url': self.clientarea_url + tds[5].div.a['href'].split('.php')[1],
            })
        return self.services

    @staticmethod
    def _extract_service_info(html):
        soup = BeautifulSoup(html, 'lxml')
        domain = soup.find('div', {'id': 'tab1'}).find('div', {'class': 'col70'}).div
        info = []
        for content in domain.findAll('h4', recursive=False):
            if content.nextSibling:
                info.append(content.nextSibling.strip())
        return info
