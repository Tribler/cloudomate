from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import int

from future import standard_library
from mechanicalsoup import LinkNotFoundError

from cloudomate.gateway.bitpay import BitPay
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.vps_hoster import VpsOption

standard_library.install_aliases()


class CrownCloud(SolusvmHoster):
    CART_URL = 'https://crowncloud.net/clients/cart.php?a=view'
    OPTIONS_URL = 'http://crowncloud.net/openvz.php'

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_clientarea_url():
        return 'https://crowncloud.net/clients/clientarea.php'

    @staticmethod
    def get_gateway():
        return BitPay

    @staticmethod
    def get_metadata():
        return "CrownCloud", "https://crowncloud.net/"

    @staticmethod
    def get_required_settings():
        return {
            'user': [
                'firstname',
                'lastname',
                'email',
                'password',
                'phonenumber',
            ],
            'address': [
                'address',
                'city',
                'state',
                'zipcode',
            ],
            'server': [
                'root_password'
            ]
        }

    '''
    Action methods of the Hoster that can be called
    '''

    @classmethod
    def get_options(cls):
        browser = cls._create_browser()
        browser.open(cls.OPTIONS_URL)

        # Get all pricing boxes
        page = browser.get_current_page()
        return list(cls._parse_options(page))

    def purchase(self, wallet, option):
        self._browser.open(option.purchase_url)
        self._submit_server_form()
        self._browser.open(self.CART_URL)
        page = self._submit_user_form()
        self.pay(wallet, self.get_gateway(), page.url)

    '''
    Hoster-specific methods that are needed to perform the actions
    '''

    @classmethod
    def _parse_options(cls, page):
        tables = page.findAll('table')
        for table in tables:  # There are multiple tables with server options on the page
            for row in table.findAll('tr'):
                if len(row.findAll('td')) > 0:  # Ignore headers
                    option = cls._parse_row(row)
                    if option is not None:
                        yield option

    @staticmethod
    def _parse_row(row):
        details = row.findAll('td')

        name = details[0].text

        price = details[6].text
        if 'yearly only' in price:
            return None  # Only yearly price possible
        try:
            i = price.index('/')
        except ValueError:
            return None  # Invalid price string
        price = int(price[1:i])

        cores = int(details[3].text[0])

        memory = float(details[1].text[0:4]) / 1000

        storage = details[2].text.split(' GB')
        storage = int(storage[0])

        bandwidth = details[4].text.split(' GB')
        bandwidth = bandwidth[0]

        connection = details[4].text
        i = connection.index('Gbps')
        connection = int(connection[i - 1])

        purchase_url = details[7].find('a')['href']

        return VpsOption(name, cores, memory, storage, bandwidth, connection, price, purchase_url)

    def _submit_server_form(self):
        try:
            form = self._browser.select_form('form#orderfrm')
            self._fill_server_form()

            form.form['action'] = 'https://crowncloud.net/clients/cart.php'
            print("Frm1")
            # form.form['method'] = 'post'
        except LinkNotFoundError:
            print("Frm2")
            form = self._browser.select_form('form#frmConfigureProduct')
            self._fill_server_form()

        form['billingcycle'] = 'monthly'
        form['configoption[1]'] = '56'
        form['configoption[8]'] = '52'

        try:  # The extra bandwidth option is not always available
            form['configoption[9]'] = '0'
        except LinkNotFoundError:
            pass

        return self._browser.submit_selected()

    def _submit_user_form(self):
        # Select the correct submit button
        form = self._browser.select_form('form#frmCheckout')
        soup = self._browser.get_current_page()
        submit = soup.select('button#btnCompleteOrder')[0]
        form.choose_submit(submit)

        # Let SolusVM handle the rest
        gateway = self.get_gateway()
        self._fill_user_form(gateway.get_name(), errorbox_class='errorbox')

        # Redirect to BitPay
        self._browser.select_form(nr=0)
        return self._browser.submit_selected()
