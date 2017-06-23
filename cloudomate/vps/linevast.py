import itertools
import json
import sys
import urllib
from collections import OrderedDict

from bs4 import BeautifulSoup
from mechanize import ControlNotFoundError

from cloudomate.gateway import bitpay
from cloudomate.vps.clientarea import ClientArea
from cloudomate.vps.solusvm_hoster import SolusvmHoster
from cloudomate.vps.vpsoption import VpsOption


class LineVast(SolusvmHoster):
    name = "linevast"
    website = "https://linevast.de/"
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
    ]
    clientarea_url = 'https://panel.linevast.de/clientarea.php'
    gateway = bitpay

    def __init__(self):
        super(LineVast, self).__init__()

    def register(self, user_settings, vps_option):
        """
        Register RockHoster provider, pay through CoinBase
        :param user_settings: 
        :param vps_option: 
        :return: 
        """
        self.br.open(vps_option.purchase_url)
        self.server_form(user_settings)
        self.br.open('https://panel.linevast.de/cart.php?a=view')
        self.br.follow_link(text_regex=r'Checkout')
        self.br.select_form(name='orderfrm')
        self.user_form(self.br, user_settings, self.gateway.name)
        self.br.select_form(nr=0)
        page = self.br.submit()
        return self.gateway.extract_info(page.geturl())

    def server_form(self, user_settings):
        """
        Fills in the form containing server configuration.
        :return: 
        """
        self.select_form_id(self.br, 'frmConfigureProduct')
        self.fill_in_server_form(self.br.form, user_settings, rootpw=False, hostname=False, nameservers=False)
        try:
            self.br.form['configoption[61]'] = ['657']  # Ubuntu 16.04
        except ControlNotFoundError:
            self.br.form['configoption[125]'] = ['549']  # Ubuntu 16.04
        self.br.submit()

    def start(self):
        """
        Linux (OpenVZ) and Windows (KVM) pages are slightly different, therefore their pages are parsed by different 
        methoods. Windows configurations allow a selection of Linux distributions, but not vice-versa.
        :return: possible configurations.
        """
        openvz_hosting_page = self.br.open("https://linevast.de/angebote/linux-openvz-vserver-mieten.html")
        options = self.parse_openvz_hosting(openvz_hosting_page.get_data())

        # kvm_hosting_page = self.br.open("https://linevast.de/angebote/kvm-vserver-mieten.html")
        # options = itertools.chain(options, self.parse_kvm_hosting(kvm_hosting_page.get_data()))
        return options

    def parse_openvz_hosting(self, page):
        soup = BeautifulSoup(page, "lxml")
        table = soup.find('table', {'class': 'plans-block'})
        details = table.tbody.tr
        names = table.findAll('div', {'class': 'plans-title'})
        i = 0
        for plan in details.findAll('div', {'class': 'plans-content'})[1:]:
            name = names[i].text.strip() + ' OVZ'
            option = self.parse_openvz_option(plan, name)
            i = i + 1
            yield option

    @staticmethod
    def parse_openvz_option(plan, name):
        elements = plan.findAll("div", {'class': 'info'})
        option = VpsOption(
            name=name,
            storage=elements[0].text.split(' GB')[0],
            cpu=elements[1].text.split(' vCore')[0],
            ram=elements[2].text.split(' GB')[0],
            bandwidth='unmetered',
            currency='EUR',
            connection=int(elements[4].text.split(' GB')[0]) * 1000,
            price=float(plan.find('div', {'class': 'plans-price'}).span.text.replace(u'\u20AC', '')),
            purchase_url=plan.a['href'],
        )
        return option

    def parse_kvm_hosting(self, page):
        soup = BeautifulSoup(page, "lxml")
        table = soup.find('table', {'class': 'plans-block'})
        details = table.tbody.tr
        names = table.findAll('div', {'class': 'plans-title'})
        i = 0
        for plan in details.findAll('div', {'class': 'plans-content'})[1:]:
            name = names[i].text.strip() + ' KVM'
            option = self.parse_kvm_option(plan, name)
            i = i + 1
            yield option

    @staticmethod
    def parse_kvm_option(plan, name):
        elements = plan.findAll("div", {'class': 'info'})
        option = VpsOption(
            name=name,
            storage=elements[0].text.split(' GB')[0],
            cpu=elements[1].text.split(' vCore')[0],
            ram=elements[3].text.split(' GB')[0],
            currency='EUR',
            bandwidth='unmetered',
            connection=int(elements[4].text.split(' GB')[0]) * 1000,
            price=float(plan.find('div', {'class': 'plans-price'}).span.text.replace(u'\u20AC', '')),
            purchase_url=plan.a['href'],
        )
        return option

    def get_status(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        return clientarea.print_services()

    def set_rootpw(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        info = clientarea.get_service_info()
        self.br.open("https://vm.linevast.de/login.php")
        self.br.select_form(nr=0)
        self.br.form['username'] = info[2]
        self.br.form['password'] = info[3]
        self.br.form.new_control('text', 'Submit', {'name': 'Submit', 'value': '1'})
        self.br.form.new_control('text', 'act', {'name': 'act', 'value': 'login'})
        self.br.form.method = "POST"
        page = self.br.submit()
        if not self._check_login(page.get_data()):
            print("Login failed")
            sys.exit(2)
        self.br.open("https://vm.linevast.de/home.php")
        vi = self._extract_vi_from_links(self.br.links())
        data = {
            'act': 'rootpassword',
            'opt': user_settings.get('rootpw'),
            'vi': vi
        }
        data = urllib.urlencode(data)
        page = self.br.open("https://vm.linevast.de/_vm_remote.php", data)
        if not self._check_set_rootpw(page.get_data()):
            print("Setting password failed")
            sys.exit(2)
        else:
            print("Password changed successfully")

    @staticmethod
    def _extract_vi_from_links(links):
        for link in links:
            if "_v=" in link.url:
                return link.url.split("_v=")[1]
        return False

    @staticmethod
    def _check_set_rootpw(text):
        data = json.loads(text)
        if data['success'] and data['success'] == '1' \
                and data['updtype'] and data['updtype'] == '1' \
                and data['apistate'] and data['apistate'] == '1':
            return True
        return False

    @staticmethod
    def _check_login(text):
        data = json.loads(text)
        if data['success'] and data['success'] == '1':
            return True
        return False

    def get_ip(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        return clientarea.get_ip()

    def info(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        data = clientarea.get_service_info()
        return OrderedDict([
            ('Hostname', data[0]),
            ('IP address', data[1]),
            ('Control panel', 'https://vm.linevast.de/'),
            ('Username', data[2]),
            ('Password', data[3]),
        ])
