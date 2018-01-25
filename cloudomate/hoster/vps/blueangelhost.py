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

from cloudomate.gateway.bitpay import BitPay
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.vps_hoster import VpsOption
from cloudomate.hoster.vps.vps_hoster import VpsStatus
from cloudomate.hoster.vps.vps_hoster import VpsStatusResource

standard_library.install_aliases()


class BlueAngelHost(SolusvmHoster):
    CLIENT_DATA_URL = 'https://www.billing.blueangelhost.com/modules/servers/solusvmpro/get_client_data.php'
    CART_URL = 'https://www.billing.blueangelhost.com/cart.php?a=view'

    def __init__(self, settings):
        super(BlueAngelHost, self).__init__(settings)

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_clientarea_url():
        return 'https://www.billing.blueangelhost.com/clientarea.php'

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

    def get_status(self):
        status = super().get_status()

        # Retrieve the vserverid
        page = self._browser.open(status.clientarea.url)
        match = re.search(r'vserverid = (\d+)', page.text)
        identifier = match.group(1)

        millis = int(round(time.time() * 1000))  # Needed for some reason
        page = self._browser.open('{}?vserverid={}&_={}'.format(self.CLIENT_DATA_URL, identifier, millis))
        data = page.json()

        memory = VpsStatusResource(self._convert_gigabyte(data['memoryused']),
                                   self._convert_gigabyte(data['memorytotal']))
        storage = VpsStatusResource(self._convert_gigabyte(data['hddused']), self._convert_gigabyte(data['hddtotal']))
        bandwidth = VpsStatusResource(self._convert_gigabyte(data['bandwidthused']),
                                      self._convert_gigabyte(data['bandwidthtotal']))

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
        self.pay(wallet, self.get_gateway(), self._browser.get_url())

    '''
    Hoster-specific methods that are needed to perform the actions
    '''

    @staticmethod
    def _convert_gigabyte(s):
        n = float(s.split(' ')[0])
        if 'KB' in s:
            n /= 1024.0 * 1024.0
        elif 'MB' in s:
            n /= 1024.0
        elif 'GB' in s:
            pass
        elif 'TB' in s:
            n *= 1024.0
        else:
            raise ValueError('Unknown unit in string {}'.format(s))

        return n

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
        form['configoption[72]'] = '87'  # Ubuntu
        form['configoption[73]'] = '91'  # 64 bit
        self._browser.submit_selected()
