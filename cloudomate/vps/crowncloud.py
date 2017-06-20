import re
import sys
from collections import OrderedDict

from bs4 import BeautifulSoup

import cloudomate.gateway.bitpay
from cloudomate.vps.clientarea import ClientArea
from cloudomate.vps.solusvm_hoster import SolusvmHoster
from cloudomate.vps.vpsoption import VpsOption
from cloudomate.wallet import determine_currency


class CrownCloud(SolusvmHoster):
    name = "crowncloud"
    website = "http://crowncloud.net/"
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
        'rootpw'
    ]
    clientarea_url = 'https://crowncloud.net/clients/clientarea.php'
    gateway = cloudomate.gateway.bitpay

    def __init__(self):
        super(CrownCloud, self).__init__()

    def register(self, user_settings, vps_option):
        """
        Register CrownCloud provider, pay through BitPay
        :param user_settings: 
        :param vps_option: 
        :return: 
        """
        self.br.open("https://crowncloud.net")
        self.br.open(vps_option.purchase_url)
        self.server_form(user_settings)
        self.br.open('https://crowncloud.net/clients/cart.php?a=view')
        self.select_form_id(self.br, 'frmCheckout')
        promobutton = self.br.form.find_control(type="submitbutton", nr=0)
        promobutton.disabled = True
        self.user_form(self.br, user_settings, self.gateway.name, errorbox_class='errorbox')
        self.br.select_form(nr=0)
        page = self.br.submit()
        return self.gateway.extract_info(page.geturl())

    def server_form(self, user_settings):
        """
        Fills in the form containing server configuration.
        :return: 
        """
        self.select_form_id(self.br, 'orderfrm')
        self.fill_in_server_form(self.br.form, user_settings, nameservers=False, rootpw=False, hostname=False)
        self.br.form['configoption[1]'] = ['56']
        self.br.form['configoption[8]'] = ['52']
        self.br.form['configoption[9]'] = '0'
        self.br.submit()

    def start(self):
        clown_page = self.br.open('http://crowncloud.net/openvz.php')
        return self.parse_options(clown_page)

    def parse_options(self, page):
        soup = BeautifulSoup(page, 'lxml')
        tables = soup.findAll('table')
        for details in tables:
            for column in details.findAll('tr'):
                if len(column.findAll('td')) > 0:
                    yield self.parse_clown_options(column)

    @staticmethod
    def beautiful_bandwidth(bandwidth):
        if bandwidth == '512 GB':
            return 0.5
        else:
            return float(bandwidth.split('T')[0])

    @staticmethod
    def parse_clown_options(column):
        elements = column.findAll('td')
        ram = elements[1].text.split('/')[0]
        ram = float(ram.split('M')[0]) / 1024
        price = elements[8].text
        price = price.split('$')[1]
        price = float(price.split('/')[0])

        return VpsOption(
            name=elements[0].text,
            ram=ram,
            storage=float(elements[2].text.split('G')[0]),
            cpu=int(elements[3].text.split('v')[0]),
            bandwidth=CrownCloud.beautiful_bandwidth(elements[4].text),
            connection=int(elements[7].text.split('G')[0]) * 1000,
            price=price,
            currency=determine_currency(elements[8].text),
            purchase_url=elements[9].find('a')['href']
        )

    def get_status(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        return clientarea.print_services()

    def set_rootpw(self, user_settings):
        print("CrownCloud does not support changing root password through their configuration panel.")
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        (ip, user, rootpw) = self._extract_vps_information(clientarea)
        print("IP: %s" % ip)
        print("Root password: %s\n" % rootpw)

        print("https://crownpanel.com")
        print("Username: %s" % user)
        print("Password: %s\n" % rootpw)

    def _extract_vps_information(self, clientarea):
        emails = clientarea.get_emails()
        for email in emails:
            if 'New VPS Information' in email['title']:
                page = self.br.open("https://crowncloud.net/clients/viewemail.php?id=" + email['id'])
                (ip, user, rootpw) = self._extract_email_info(page.get_data())
                return ip, user, rootpw
        return None

    @staticmethod
    def _extract_email_info(data):
        soup = BeautifulSoup(data, 'lxml')
        text = soup.find('td', {'class': 'bodyContent'}).text
        ip_match = re.search(r'Main IP: (\d+\.\d+\.\d+\.\d+)', text)
        user_match = re.search(r'Username: (\w+)', text)
        rootpw = re.search(r'Root Password: (\w+)You', text)
        return ip_match.group(1), user_match.group(1), rootpw.group(1)

    def get_ip(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        (ip, user, rootpw) = self._extract_vps_information(clientarea)
        if not ip:
            print("No active IP found")
            sys.exit(2)
        return ip

    def info(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        (ip, user, rootpw) = self._extract_vps_information(clientarea)
        return OrderedDict([
            ('IP address', ip),
            ('Control panel', 'https://crownpanel.com/'),
            ('Username', user),
            ('Password', rootpw),
        ])
