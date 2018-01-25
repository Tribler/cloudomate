from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
from builtins import int

from future import standard_library

from cloudomate.gateway.undergroundprivate import UndergroundPrivate as UndergroundPrivateGateway
from cloudomate.hoster.vps import vps_hoster
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster

standard_library.install_aliases()


class UndergroundPrivate(SolusvmHoster):
    CART_URL = 'https://www.clientlogin.sx/cart.php?a=view'
    OPTIONS_URL = 'https://undergroundprivate.com/russiaoffshorevps.html'

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_clientarea_url():
        return 'https://www.clientlogin.sx/clientarea.php'

    @staticmethod
    def get_gateway():
        return UndergroundPrivateGateway

    @staticmethod
    def get_metadata():
        return 'UndergroundPrivate', 'https://undergroundprivate.com'

    @staticmethod
    def get_required_settings():
        return {
            'user': ['firstname', 'lastname', 'email', 'phonenumber', 'password'],
            'address': ['address', 'city', 'state', 'zipcode', 'countrycode'],
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
        boxes = soup.select('div.pricingboxes > div.row > div > ul')
        boxes = boxes[:-1]  # Remove last item, which is a custom server and can't be bought automatically
        options = [cls._parse_box(box) for box in boxes]

        # Remove options that are out of stock
        # Cookies are no problem, since this method used its own browser
        filtered_options = []
        for option in options:
            page = browser.open(option.purchase_url)
            if 'add' not in page.url:
                # Not out of stock!
                filtered_options.append(option)
        return filtered_options

    def purchase(self, wallet, option):
        self._browser.open(option.purchase_url)
        self._submit_server_form()
        self._browser.open(self.CART_URL)
        self._submit_user_form()

        # Retrieve the payment URL from an iFrame
        soup = self._browser.get_current_page()
        iframe = soup.select_one('iframe')
        url = iframe['src']

        self.pay(wallet, self.get_gateway(), url)

    '''
    Hoster-specific methods that are needed to perform the actions
    '''

    @staticmethod
    def _parse_box(box):
        details = box.findAll('li')

        name = details[0].text.rstrip()

        price = details[1].span.text
        price = float(price[1:])

        cores = details[2].text
        cores = cores.split('\n')
        cores = int(cores[1][0])

        memory = details[4].text
        memory = float(memory[0])

        storage = details[3].text
        gb_index = storage.index('GB')
        storage = storage[0:gb_index]

        connection = details[6].text
        connection = int(connection[0])

        purchase_url = details[-1].p.span.a['href']

        return vps_hoster.VpsOption(name, cores, memory, storage, sys.maxsize, connection, price, purchase_url)

    def _submit_server_form(self):
        form = self._browser.select_form('form#orderfrm')

        self._fill_server_form()
        form['billingcycle'] = 'monthly'
        form['configoption[7]'] = '866'  # Operating System: Ubuntu 16.04
        form['configoption[8]'] = '54'  # Control Panel: None
        form['configoption[9]'] = '56'  # Extra IP Address: None
        form['configoption[94]'] = '869'  # Manual setup
        form.form['action'] = 'https://www.clientlogin.sx/cart.php'
        form.form['method'] = 'get'

        return self._browser.submit_selected()

    def _submit_user_form(self):
        # Select the correct submit button
        form = self._browser.select_form('form#frmCheckout')
        soup = self._browser.get_current_page()
        submit = soup.select_one('button#btnCompleteOrder')
        form.choose_submit(submit)

        # Let SolusVM class handle the rest
        gateway = self.get_gateway()
        return self._fill_user_form(gateway.get_name(), errorbox_class='errorbox')
