from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import super

from future import standard_library
from mechanicalsoup.utils import LinkNotFoundError

from cloudomate.gateway.coinpayments import CoinPayments
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.vps_hoster import VpsOption

standard_library.install_aliases()


class LibertyVPS(SolusvmHoster):
    CART_URL = 'https://support.routerhosting.com/cart.php?a=view'

    # true if you can enable tuntap in the control panel
    TUN_TAP_SETTINGS = True

    _settings = None
    _controlpanel = None

    def __init__(self, settings):
        super(LibertyVPS, self).__init__(settings)

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_clientarea_url():
        return 'https://support.routerhosting.com/clientarea.php'

    @staticmethod
    def get_gateway():
        return CoinPayments

    @staticmethod
    def get_metadata():
        return 'libertyvps', 'https://libertyvps.net/'

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
        """
        Linux (OpenVZ) and Windows (KVM) pages are slightly different, therefore their pages are parsed by different
        methods. Windows configurations allow a selection of Linux distributions, but not vice-versa.
        :return: possible configurations.
        """
        browser = cls._create_browser()
        browser.open("https://libertyvps.net/offshore-vps")
        options = cls._parse_openvz_hosting(browser.get_current_page())
        lst = list(options)

        return lst

    def purchase(self, wallet, option):
        self._browser.open(option.purchase_url)
        self._server_form()
        self._browser.open(self.CART_URL)

        summary = self._browser.get_current_page().find('div', class_='summary-container')
        self._browser.follow_link(summary.find('a', class_='btn-checkout'))

        try:
            self._browser.select_form(selector='form#frmCheckout')
        except LinkNotFoundError:
            print("Too many open transactions, try connecting from a different IP")
            raise

        self._fill_user_form(self.get_gateway().get_name())

        self._browser.select_form(nr=0)  # Go to payment form
        self._browser.submit_selected()

        return self.pay(wallet, self.get_gateway(), self._browser.get_url(), self._browser, self._settings)

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
        form['configoption[46]'] = '365'  # Ubuntu 16.04
        self._browser.submit_selected()

    @classmethod
    def _parse_openvz_hosting(cls, page):
        table = page.find('div', {'class': 'uds-pricing-table default '})
        thead = page.find('thead')
        tfoot = page.find('tfoot')
        number_of_entries = len(table.find('tr', {'class': 'even'}).find_all('td'))

        for idx in range(1, number_of_entries+1):
            header_elements = thead.find_all('tr')[1].find('th', {'class': 'column-' + str(idx)}).find_all('p')
            list_elements = table.find_all('td', {'class': 'column-' + str(idx)})
            link_element = tfoot.find('th', {'class': 'column-' + str(idx)})

            print(header_elements)
            print(list_elements)
            print(link_element)
            # price_eur = float(option.find('div', {'class', 'price'}).span.text[1:])
            # c = CurrencyConverter()
            # price_usd = float(option.find('', {'class', 'price'}).span.text[1:])
            # list_elements[2].text.strip().split(' ')[0],
            yield VpsOption(
                name=header_elements[0].text,
                storage=list_elements[2].text.strip().split('GB')[0],
                cores=list_elements[0].text.strip().split(' ')[0].split('\xa0')[0],
                memory=list_elements[1].text.strip().split(' ')[0],
                bandwidth=list_elements[3].text.strip(),
                connection=list_elements[4].text.strip().split('Gbps')[0],
                price=float(header_elements[1].text[1:]),
                purchase_url=link_element.find('a')['href'],
            )
