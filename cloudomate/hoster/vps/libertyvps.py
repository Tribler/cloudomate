from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import super

from future import standard_library
from mechanicalsoup.utils import LinkNotFoundError

from cloudomate.hoster.vps.clientarea import ClientArea
from cloudomate.gateway.coinpayments import CoinPayments
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.vps_hoster import VpsConfiguration
from cloudomate.hoster.vps.vps_hoster import VpsOption

standard_library.install_aliases()


class LibertyVPS(SolusvmHoster):
    CART_URL = 'https://libertyvps.net/clients/cart.php?a=view'

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
        return 'https://libertyvps.net/clients/clientarea.php'

    @staticmethod
    def get_email_url():
        return 'https://libertyvps.net/clients/viewemail.php'  # + ?id=123456

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
        forms = self._browser.get_current_page().find_all('form')
        self._browser.select_form(forms[2])
        self._browser.submit_selected()

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
        form = self._browser.select_form('form')

        self._fill_server_form()
        form['configoption[1]'] = '4'  # Ubuntu 16.04
        self._browser.submit_selected()

    @classmethod
    def _parse_openvz_hosting(cls, page):
        table = page.find('div', {'class': 'uds-pricing-table'})
        thead = page.find('thead')
        tfoot = page.find('tfoot')
        number_of_entries = len(table.find('tr', {'class': 'even'}).find_all('td'))

        for idx in range(1, number_of_entries + 1):
            header_elements = thead.find_all('tr')[1].find('th', {'class': 'column-' + str(idx)}).find_all('p')
            list_elements = table.find_all('td', {'class': 'column-' + str(idx)})
            link_element = tfoot.find('th', {'class': 'column-' + str(idx)})

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

    def get_configuration(self):
        clientarea = self._create_clientarea()

        ip = clientarea.get_server_information_from_email()['ip_address']
        password = clientarea.get_server_information_from_email()['server_password']

        return VpsConfiguration(ip, password)

    def _create_clientarea(self):
        if self._clientarea is None:
            self._clientarea = LibertyVPSClientArea(self.get_browser(), self.get_clientarea_url(),
                                                    self.get_email_url(), self._settings)
        return self._clientarea


class LibertyVPSClientArea(ClientArea):
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
        email_id = self._get_email_id()
        self._browser.open(self.email_url + '?id=' + email_id)
        soup = self._browser.get_current_page()

        server_info = {
            'ip_address': None,
            'server_user': None,
            'server_password': None,
        }

        body = soup.find('div', {'class': 'panel-body main-content'}).text
        server_info['server_user'] = 'root'
        server_info['server_password'] = body.split('root password: ')[1].split('\n')[0]
        server_info['ip_address'] = body.split('Main IP: ')[1].split('\n')[0]

        return server_info

    def _get_email_id(self):
        for email in self.get_emails():
            e_id = email['id']
            title = email['title']
            if title == 'Your new server login details':
                return e_id

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
