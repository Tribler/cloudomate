from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import re
import time

from builtins import int
from builtins import super

from future import standard_library
from mechanicalsoup.utils import LinkNotFoundError

from cloudomate.gateway.blockchain import Blockchain
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.vps_hoster import VpsOption
from cloudomate.hoster.vps.vps_hoster import VpsConfiguration
from cloudomate.hoster.vps.clientarea import ClientArea

standard_library.install_aliases()


class TwoSync(SolusvmHoster):
    CART_URL = 'https://ua.2sync.org/cart.php?a=view'

    def __init__(self, settings):
        super(TwoSync, self).__init__(settings)

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_clientarea_url():
        return 'https://ua.2sync.org/clientarea.php'

    @staticmethod
    def get_email_url():
        return 'https://ua.2sync.org/viewemail.php'

    @staticmethod
    def get_gateway():
        return Blockchain

    @staticmethod
    def get_metadata():
        return 'twosync', 'https://www.2sync.co/vps/ukraine/'

    @staticmethod
    def get_required_settings():
        return {
            'user': ['firstname', 'lastname', 'email', 'phonenumber', 'password'],
            'address': ['address', 'city', 'state', 'zipcode'],
        }

    def _create_clientarea(self):
        if self._clientarea is None:
            self._clientarea = TSClientArea(self.get_browser(), self.get_clientarea_url(),
                                                  self.get_email_url(), self._settings)
        return self._clientarea

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
        browser.open("https://www.2sync.co/vps/ukraine/")

        options = cls._parse_openvz_hosting(browser.get_current_page())
        lst = list(options)

        return lst

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

    def enable_tun_tap(self):
        """
        TwoSync already has tuntap enabled
        :return: True
        """
        return True

    def purchase(self, wallet, option):
        self._browser.open(option.purchase_url)
        self._server_form()
        self._browser.open(self.CART_URL)

        summary = self._browser.get_current_page().find('div', class_='summary-container')
        self._browser.follow_link(summary.find('a', class_='btn-checkout'))

        form = self._browser.select_form(selector='form#frmCheckout')
        self._fill_user_form(self.get_gateway().get_name())

        self._browser.select_form(nr=0)  # Go to payment form
        self._browser.submit_selected()

        self._browser.open('https://ua.2sync.org/cart.php?a=complete')
        invoice = self._browser.get_current_page().find('a', {'class': 'alert-link'})
        self._browser.follow_link(invoice)

        url = self._browser.get_url()
        urlselected = self.extract_info(url)

        self.pay(wallet, self.get_gateway(), urlselected)

        #open invoice page after paying
        invoice = str(url).split('=')[1]
        self._browser.open('https://ua.2sync.org/modules/gateways/blockchain.php?invoice=' + invoice)

        msoup = self._browser.get_current_page()
        mpattern = re.compile(r'secret:\s*\'(.+?)\'')
        secret = mpattern.search(str(msoup)).group(1)

        okdata = {
            'invId': invoice,
            'am': urlselected.split('&')[0],
            'secret': secret
        }

        # wait 10s to allow for payment to go through
        print("Waiting 10s before 'clicking' on OK...")
        time.sleep(10)

        # this emulates a mouse click on the "OK" button
        self._browser.session.post(url='https://ua.2sync.org/blockchain_openTicket.php', data=okdata)

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
            form['configoption[5]'] = '14'  # Ubuntu 16.04
        except LinkNotFoundError:
            print('error')
        self._browser.submit_selected()

    @classmethod
    def _parse_openvz_hosting(cls, page):
        urls = cls._get_hrefs()
        table = page.find_all('td')

        names = ['2S VSUA01', '2S VSUA02', '2S VSUA03', '2S VSUA04']
        for i in range(0, len(urls)):
            option = cls._parse_linux_option(urls[i], table, names[i], i)
            yield option


    @staticmethod
    def _parse_linux_option(url, table, name, i):
        option = VpsOption(
            name=name,
            storage=str(table[3 + (i*8)]).split('g>')[1].split('<')[0],
            cores=str(table[1 + (i*8)]).split('g>')[1].split('<')[0],
            memory=str(table[2 + (i*8)]).split('g>')[1].split('GB')[0],
            bandwidth='unmetered',
            connection=int(str(table[5 + (i*8)]).split('g>')[1].split('Gbps')[0]) * 1000,
            price=float(str(table[7 + (i*8)]).split('$')[1].split('/mo')[0]),
            purchase_url=url,
        )
        return option

    @classmethod
    def extract_info(cls, url):
        invoice = str(url).split('=')[1]
        browser = cls._create_browser()
        browser.open('https://ua.2sync.org//modules/gateways/blockchain.php?invoice=' + invoice)
        pages = browser.get_current_page().find_all('b')
        amount = float(str(pages[0]).split('>')[1].split(' BTC')[0])
        address = str(pages[1]).split('>')[1].split('<')[0]
        return str(amount) + '&' + address


    @classmethod
    def _get_hrefs(cls):
        browser = cls._create_browser()
        browser.open("https://ua.2sync.org/cart.php")
        page = browser.get_current_page()
        hrefs = page.find_all('a', {'class': 'order-button'})
        lst = [None] * int(len(hrefs)/2)

        for x in range(0, len(hrefs), 2):
            urlstring = str(hrefs[x]).split('href="')[1].split('"')[0]
            urlstring = urlstring.replace('/cart.php', '').replace('amp;', '')
            url = browser.get_url()
            url = url.split('?')[0]
            url = url + urlstring
            lst[int(x/2)] = url

        return lst

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


class TSClientArea(ClientArea):
    """
    Modified ClientAria for twosync,
    Extended for looking up server information such as IP, root password
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
            if 'ready' in title:
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
        pattern1 = re.compile(r'(?:<.>)*((?:Username:)|(?:Root Password:)|(?:VPS IP:))\s*((?:\w{1,3}\.*){1,4})(?:<.>)*', re.MULTILINE)

        for p in ps:
            p = re.sub(r'[^\x00-\x7F]+', '', str(p)).decode('utf-8','ignore').strip()
            for (k, v) in re.findall(pattern1, p):
                if 'VPS IP' in k and not server_info['ip_address']:
                    server_info['ip_address'] = v
                elif 'Root Password' in k and not server_info['server_password']:
                    server_info['server_password'] = v
                elif 'Username' in k and not server_info['server_user']:
                    server_info['server_user'] = v

        return server_info

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
