from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
from builtins import int

from future import standard_library

from cloudomate.gateway.coinbase import Coinbase
from cloudomate.hoster.vps import vps_hoster
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster

standard_library.install_aliases()


class Pulseservers(SolusvmHoster):
    CART_URL = 'https://www.pulseservers.com/billing/cart.php?a=confdomains'
    OPTIONS_URL = 'https://pulseservers.com/vps-linux.html'

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_clientarea_url():
        return 'https://www.pulseservers.com/billing/clientarea.php'

    @staticmethod
    def get_gateway():
        return Coinbase

    @staticmethod
    def get_metadata():
        return 'PulseServers', 'https://pulseservers.com/'

    @staticmethod
    def get_required_settings():
        return {
            'user': ['firstname', 'lastname', 'email', 'phonenumber', 'password'],
            'address': ['address', 'city', 'state', 'zipcode'],
            'server': ['hostname', 'root_password']
        }

    '''
    Action methods of the Hoster that can be called
    '''

    @classmethod
    def get_options(cls):
        browser = cls._create_browser()
        browser.open(cls.OPTIONS_URL)

        # Get all pricing boxes
        soup = browser.get_current_page()
        boxes = soup.select('div.pricing-box')
        return [cls._parse_box(box) for box in boxes]

    def purchase(self, wallet, option):
        self._browser.open(option.purchase_url)
        self._submit_server_form()
        self._browser.open(self.CART_URL)
        page = self._submit_user_form()
        self.pay(wallet, self.get_gateway(), page.url)

    '''
    Hoster-specific methods that are needed to perform the actions
    '''

    def _submit_server_form(self):
        form = self._browser.select_form('form#orderfrm')

        self._fill_server_form()
        form.set('billingcycle', 'monthly')
        form.form['action'] = 'https://www.pulseservers.com/billing/cart.php'

        return self._browser.submit_selected()

    def _submit_user_form(self):
        # Select the correct submit button
        form = self._browser.select_form('form#mainfrm')
        soup = self._browser.get_current_page()
        submit = soup.select_one('input.ordernow')
        form.choose_submit(submit)

        # Let SolusVM class handle the rest
        gateway = self.get_gateway()
        self._fill_user_form(gateway.get_name(), errorbox_class='errorbox')

        # Redirect to Coinbase
        self._browser.select_form(nr=0)
        return self._browser.submit_selected()

    @staticmethod
    def _parse_box(box):
        details = box.findAll('li')

        name = details[0].h4.text

        price = details[1].h1.text
        price = float(price[1:])

        cores = details[2].strong.text
        cores = int(cores.split(' ')[0])

        memory = details[3].strong.text
        memory = float(memory[0:-2])

        storage = details[4].strong.text
        if storage == '1TB':
            storage = 1000.0
        else:
            storage = float(storage[0:-2])

        connection = details[5].strong.text
        connection = int(connection[0:-7])

        purchase_url = details[9].a['href']

        return vps_hoster.VpsOption(name, cores, memory, storage, sys.maxsize, connection, price, purchase_url)
