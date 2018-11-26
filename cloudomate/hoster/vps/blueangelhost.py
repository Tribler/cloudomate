from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools
import re
import time
from builtins import int
from builtins import super

from future import standard_library

from bs4 import Tag
from past.builtins import unicode

from cloudomate.gateway.bitpay import BitPay
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.vps_hoster import VpsOption
from cloudomate.hoster.vps.vps_hoster import VpsStatus
from cloudomate.hoster.vps.vps_hoster import VpsStatusResource
from cloudomate.hoster.vps.vps_hoster import VpsConfiguration
from cloudomate.hoster.vps.clientarea import ClientArea

standard_library.install_aliases()


class BlueAngelHost(SolusvmHoster):
    CART_URL = 'https://www.billing.blueangelhost.com/cart.php?a=view'

    # true if you can enable tuntap in the control panel
    TUN_TAP_SETTINGS = False

    def __init__(self, settings):
        super(BlueAngelHost, self).__init__(settings)

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_clientarea_url():
        return 'https://www.billing.blueangelhost.com/clientarea.php'

    @staticmethod
    def get_email_url():
        return 'https://www.billing.blueangelhost.com/viewemail.php' # + ?id=123456

    @staticmethod
    def get_gateway():
        return BitPay

    @staticmethod
    def get_metadata():
        return 'BlueAngelHost', 'https://www.blueangelhost.com/'

    @staticmethod
    def get_required_settings():
        return {
            'user': ['firstname', 'lastname', 'email', 'phonenumber', 'password'],
            'address': ['address', 'city', 'state', 'zipcode'],
            'server': ['hostname', 'root_password', 'ns1', 'ns2']
        }

    def _create_clientarea(self):
        if self._clientarea is None:
            self._clientarea = BAHClientArea(self.get_browser(), self.get_clientarea_url(),
                                                  self.get_email_url(), self._settings)
        return self._clientarea

    '''
    Action methods of the Hoster that can be called
    '''

    @classmethod
    def get_options(cls):
        browser = cls._create_browser()
        browser.open("https://www.blueangelhost.com/openvz-vps/")
        options = cls._parse_options(browser.get_current_page())

        browser.open("https://www.blueangelhost.com/kvm-vps/")
        options = itertools.chain(options, cls._parse_options(browser.get_current_page(), is_kvm=True))
        return list(options)

    def get_configuration(self):
        """
        Overrides the default configuration method as BlueAngelHost doesn't use the server password during
        registration
        :return: IP and Password
        """
        server_info = self.get_clientarea().get_server_information_from_email()
        ip = server_info.get('ip_address')
        password = server_info.get('server_password')

        return VpsConfiguration(ip, password)

    def get_status(self):
        status = super().get_status()

        # Get server stats
        page = self._browser.open('{}&api=json&act=vpsmanage&stats=1'.format(status.clientarea.url))
        data = page.json()

        memory = VpsStatusResource(data['info']['ram']['used']/1024.0,
                                   data['info']['ram']['limit']/1024.0)
        storage = VpsStatusResource(data['info']['disk']['used_gb'],
                                    data['info']['disk']['limit_gb'])
        bandwidth = VpsStatusResource(data['info']['bandwidth']['used_gb'],
                                      data['info']['bandwidth']['limit_gb'])

        return VpsStatus(memory, storage, bandwidth, status.online, status.expiration, status.clientarea)

    def purchase(self, wallet, option):
        self._browser.open(option.purchase_url)
        self._submit_server_form()
        self._browser.open(self.CART_URL)
        summary = self._browser.get_current_page().find('div', class_='summary-container')
        self._browser.follow_link(summary.find('a', class_='btn-checkout'))

        self._browser.select_form(selector='form[name=orderfrm]')
        self._browser.get_current_form()['customfield[4]'] = 'Google'
        self._fill_user_form(self.get_gateway().get_name())

        self._browser.select_form(nr=0)
        self._browser.submit_selected()
        return self.pay(wallet, self.get_gateway(), self._browser.get_url())

    '''
    Hoster-specific methods that are needed to perform the actions
    '''

    @classmethod
    def _parse_options(cls, page, is_kvm=False):
        month = page.find('div', {'id': 'monthly_price'})
        details = month.findAll('div', {'class': 'plan_table'})
        for column in details:
            yield cls._parse_blue_options(column, is_kvm=is_kvm)

    @staticmethod
    def _parse_blue_options(column, is_kvm=False):
        if is_kvm:
            split_char = ' '
        else:
            split_char = ':'

        price = column.find('div', {'class': 'plan_price_m'}).text.strip()
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
            cores=int(cpu.split('C')[0].strip()),
            memory=float(ram.split('G')[0].strip()),
            storage=float(storage.split('G')[0].strip()),
            connection=int(connection.split('G')[0].strip()) * 1000,
            bandwidth=float(bandwidth.split('T')[0].strip()),
            purchase_url=column.find('a')['href']
        )

    def _submit_server_form(self):
        """
        Fills in the form containing server configuration
        :return:
        """
        form = self._browser.select_form('form#frmConfigureProduct')
        self._fill_server_form()
        form['customfield[135]'] = 'ubuntu-16.04-x86_64'  # Ubuntu 64 bit
        self._browser.submit_selected()

class BAHClientArea(ClientArea):
    """
    Modified ClientAria for BlueAngelHost,
    Extended for looking up server information and control panel credentials
    """
    email_url = None

    def __init__(self, browser, clientarea_url, email_url, user_settings):
        self.email_url = email_url
        ClientArea.__init__(self, browser, clientarea_url, user_settings)

    def get_emails(self):
        """
        Returns a list of dicts containing email metadata: {id, title}
        This can be used to further select certains emails to parse
        """
        self._browser.open(self._url + "?action=emails")
        soup = self._browser.get_current_page()
        extracted = self._extract_emails(soup)
        return extracted

    def get_server_information_from_email(self):
        """
        Returns the parsed server information from email
        """
        email_id = None
        for email in self.get_emails():
            e_id = email['id']
            title = email['title']
            if 'ready' in title.lower():
                email_id = e_id
                break
        self._browser.open(self.email_url + '?id=' + email_id)
        soup = self._browser.get_current_page()

        server_info = {
            'ip_address': None,
            'server_user': None,
            'server_password': None,
            'vmuser': None,
            'vmuser_password': None,
            'control_panel_url': None
        }


        ps = soup.findAll('p')

        # map of server_info fields to the labels in the e-mail
        server_keyword = 'Hostname'
        server_fields = {
            'ip_address': 'Main IP',
            'server_user': 'Username',
            'server_password': 'Root Password'
        }

        vm_keyword = 'Manager Details'
        vm_fields = {
            'vmuser': 'Username',
            'vmuser_password': 'Password'
        }

        for p in ps:
            for line in p:
                self._parse_email_section(p, line, server_keyword, server_fields, server_info)
                self._parse_email_section(p, line, vm_keyword, vm_fields, server_info)
                if isinstance(line, Tag) and line.name == 'a':
                    server_info['control_panel_url'] = unicode(line.next)

        return server_info

    @staticmethod
    def _parse_email_section(p, line, keyword, fields, server_info):
        if keyword in p.text:
            for key, label in fields.items():
                line_str = unicode(line)
                if label in line_str:
                    server_info[key] = line_str.split(':')[1].strip()

    @staticmethod
    def _extract_emails(soup):
        table = soup.find('table', {'id': 'tableEmailsList'}).tbody
        emails = []
        for row in table.findAll('tr'):
            emails.append({
                'id': row['onclick'].split('\'')[1].split('id=')[1],
                'title': row.findAll('td')[1].text
            })
        return emails
