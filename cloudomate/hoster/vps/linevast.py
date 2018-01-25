from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools
import json
from builtins import int
from builtins import round
from builtins import super

from forex_python.converter import CurrencyRates
from future import standard_library
from mechanicalsoup.utils import LinkNotFoundError

from cloudomate.gateway.bitpay import BitPay
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.vps_hoster import VpsOption

standard_library.install_aliases()


class LineVast(SolusvmHoster):
    CART_URL = 'https://panel.linevast.de/cart.php?a=view'

    def __init__(self, settings):
        super(LineVast, self).__init__(settings)

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_clientarea_url():
        return 'https://panel.linevast.de/clientarea.php'

    @staticmethod
    def get_gateway():
        return BitPay

    @staticmethod
    def get_metadata():
        return 'linevast', 'https://linevast.de/'

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
        browser.open("https://linevast.de/en/offers/ddos-protected-vps-hosting.html")
        options = cls._parse_openvz_hosting(browser.get_current_page())

        browser.open("https://linevast.de/en/offers/windows-vps-hosting.html")
        options = itertools.chain(options, cls._parse_kvm_hosting(browser.get_current_page()))

        return list(options)

    def purchase(self, wallet, option):
        self._browser.open(option.purchase_url)
        self._server_form()
        self._browser.open(self.CART_URL)

        summary = self._browser.get_current_page().find('div', class_='summary-container')
        self._browser.follow_link(summary.find('a', class_='btn-checkout'))

        form = self._browser.select_form(selector='form#frmCheckout')
        form['acceptdomainwiderruf1'] = True
        form['acceptdomainwiderruf2'] = True
        self._fill_user_form(self.get_gateway().get_name())

        self._browser.select_form(nr=0)  # Go to payment form
        self._browser.submit_selected()
        self.pay(wallet, self.get_gateway(), self._browser.get_url())

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
        try:
            form['configoption[61]'] = '657'  # Ubuntu 16.04
        except LinkNotFoundError:
            form['configoption[125]'] = '549'  # Ubuntu 16.04
        self._browser.submit_selected()

    @classmethod
    def _parse_openvz_hosting(cls, page):
        table = page.find('table', {'class': 'plans-block'})
        details = table.tbody.tr
        names = table.findAll('div', {'class': 'plans-title'})
        i = 0
        for plan in details.findAll('div', {'class': 'plans-content'}):
            name = names[i].text.strip() + ' OVZ'
            option = cls._parse_openvz_option(plan, name)
            i = i + 1
            yield option

    @staticmethod
    def _parse_openvz_option(plan, name):
        elements = plan.findAll("div", {'class': 'info'})
        eur = float(plan.find('div', {'class': 'plans-price'}).span.text.replace('\u20AC', ''))
        option = VpsOption(
            name=name,
            storage=elements[0].text.split(' GB')[0],
            cores=elements[1].text.split(' vCore')[0],
            memory=elements[2].text.split(' GB')[0],
            bandwidth='unmetered',
            connection=int(elements[4].text.split(' GB')[0]) * 1000,
            price=round(CurrencyRates().convert("EUR", "USD", eur), 2),
            purchase_url=plan.a['href'],
        )
        return option

    @classmethod
    def _parse_kvm_hosting(cls, page):
        table = page.find('table', {'class': 'plans-block'})
        details = table.tbody.tr
        names = table.findAll('div', {'class': 'plans-title'})
        i = 0
        for plan in details.findAll('div', {'class': 'plans-content'}):
            name = names[i].text.strip() + ' KVM'
            option = cls._parse_kvm_option(plan, name)
            i = i + 1
            yield option

    @staticmethod
    def _parse_kvm_option(plan, name):
        elements = plan.findAll("div", {'class': 'info'})
        eur = float(plan.find('div', {'class': 'plans-price'}).span.text.replace('\u20AC', ''))
        option = VpsOption(
            name=name,
            storage=elements[0].text.split(' GB')[0],
            cores=elements[1].text.split(' vCore')[0],
            memory=elements[3].text.split(' GB')[0],
            bandwidth='unmetered',
            connection=int(elements[4].text.split(' GB')[0]) * 1000,
            price=round(CurrencyRates().convert("EUR", "USD", eur), 2),
            purchase_url=plan.a['href'],
        )
        return option

    @staticmethod
    def _extract_vi_from_links(links):
        for link in links:
            if "_v=" in link.url:
                return link.url.split("_v=")[1]
        return False

    @staticmethod
    def _check_login(text):
        data = json.loads(text)
        if data['success'] and data['success'] == '1':
            return True
        return False
