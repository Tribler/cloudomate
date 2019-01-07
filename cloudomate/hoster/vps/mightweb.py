from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import sys
import time
from builtins import super

from future import standard_library

from cloudomate.gateway.bitpay import BitPay
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.vps_hoster import VpsOption

standard_library.install_aliases()


class MightWeb(SolusvmHoster):
    # true if you can enable tuntap in the control panel
    TUN_TAP_SETTINGS = False

    def __init__(self, settings):
        super(MightWeb, self).__init__(settings)

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_clientarea_url():
        return 'https://clients.hostsailor.com/clientarea.php'

    @staticmethod
    def get_gateway():
        return BitPay

    @staticmethod
    def get_metadata():
        return 'mightweb', 'https://mightweb.net/'

    @staticmethod
    def get_required_settings():
        return {
            'user': ['firstname', 'lastname', 'email', 'phonenumber', 'password'],
            'address': ['address', 'city', 'state', 'zipcode'],
        }

    '''
    Action methods of the Hoster that can be called
    '''

    @classmethod
    def get_options(cls):
        browser = cls._create_browser()
        response = browser.open("https://mightweb.net/wp-content/themes/DM/js/vps_slider.js")
        options = cls._parse_vps_servers(response.text)
        return list(options)

    @classmethod
    def _parse_vps_servers(cls, page):
        js_assignments = str(page).split('var def_pos')[0].split(';')
        data = {}
        for assignment in js_assignments:
            result = re.match(r'\s*var (\w+) = (.+)', assignment)
            if result:
                key = result.group(1)
                value = result.group(2)
                value_array_match = re.match(r'new Array\((.*)\)', value)
                if value_array_match:
                    data[key] = [value_item.replace("'", '') for value_item in value_array_match.group(1).split(',')]
                else:
                    data[key] = value.replace("'", '')

        for idx in range(len(data['Processor_Array_Linux_Unmanaged'])):
            yield VpsOption(
                name='TIER ' + str(idx + 1),
                storage=data['Storage_Array_Linux_Unmanaged'][idx].split(' ')[0],
                cores=data['Processor_Array_Linux_Unmanaged'][idx].split(' ')[0],
                memory=data['RAM_Array_Linux_Unmanaged'][idx].split(' ')[0],
                bandwidth=int(data['Bandwidth_Array_Linux_Unmanaged'][idx].split(' ')[0]) / 1000,
                connection=10,
                price=float(data['Price_Array_Linux_Unmanaged'][idx].replace('$', '')),
                purchase_url=data['b_url'] + data['Link_Array_Linux_Unmanaged'][idx]
            )

    def purchase(self, wallet, option):
        self._browser.open(option.purchase_url)
        self._browser.launch_browser()
        self._server_form()
        self._browser.open('https://my.mightweb.net/cart.php?a=view')
        link = self._browser.get_current_page().find('a', {'id': 'checkout'})
        self.get_browser().follow_link(link)

        self._browser.select_form(selector='form#frmCheckout')
        self._fill_user_form(self.get_gateway().get_name())
        self._browser.launch_browser()
        self._browser.select_form(nr=0)
        response = self._browser.submit_selected()
        # TODO: Fraud check
        print(response.text)
        print(self._browser.get_url())
        self._browser.launch_browser()
        return
        # payment_link = self._browser.get_current_page().find('form')['action']
        # print("Payment link: " + payment_link)
        return self.pay(wallet, self.get_gateway(), payment_link)

    '''
    Hoster-specific methods that are needed to perform the actions
    '''

    def _server_form(self):
        """
        Fills in the form containing server configuration.
        :return:
        """
        form = self._browser.select_form('form#frmConfigureProduct')
        self._fill_server_form()
        form['configoption[68]'] = '329'  # Ubuntu 16.04
        self._browser.submit_selected()
        page = self._browser.get_current_page()
        if page.find('li'):
            print(page.text)
            sys.exit(2)
