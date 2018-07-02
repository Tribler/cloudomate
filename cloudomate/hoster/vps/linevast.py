from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools
import json

from builtins import int
from builtins import round
from builtins import super

from future import standard_library
from mechanicalsoup.utils import LinkNotFoundError
from decimal import Decimal
from currency_converter import CurrencyConverter
import ast

from cloudomate.gateway.bitpay import BitPay
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.clientarea import ClientArea
from cloudomate.hoster.vps.vps_hoster import VpsOption

import re
import sys
import requests

standard_library.install_aliases()


class LineVast(SolusvmHoster):
    CART_URL = 'https://panel.linevast.de/cart.php?a=view'

    # true if you can enable tuntap in the control panel
    TUN_TAP_SETTINGS = True

    _settings = None
    _controlpanel = None

    def __init__(self, settings):
        super(LineVast, self).__init__(settings)

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_clientarea_url():
        return 'https://panel.linevast.de/clientarea.php'

    @staticmethod
    def get_email_url():
        return 'https://panel.linevast.de/viewemail.php' # + ?id=123456

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

    def _create_clientarea(self):
        if self._clientarea is None:
            self._clientarea = LineVastClientArea(self.get_browser(), self.get_clientarea_url(),
                                                  self.get_email_url(), self._settings)
        return self._clientarea

    def _create_controlpanel(self):
        if self._controlpanel is None:
            cl = self._create_clientarea()
            sinfo = cl.get_server_information_from_email()
            self._controlpanel = ControlPanel(self.get_browser(), sinfo['control_panel_url'],
                                              sinfo['vmuser'], sinfo['vmuser_password'])
        return self._controlpanel

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
        lst = list(options)

        return lst

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
        return self.pay(wallet, self.get_gateway(), self._browser.get_url())

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
        urls = cls._get_hrefs()
        storage = cls._get_storage()
        names = page.find_all('p', {'class': 'text-center py-3'})
        prices = page.find_all('div', {'class': 'pricing-1'})
        info = page.find_all('div', {'class': 'text-muted'})
        for i in range(0, len(info)):
            index = 2 * i + 1
            price = str(prices).split('data-monthly="')[index].split('" data-yearly=')[0]
            name = str(names[i]).split('data-product="')[1].split('" href')[0]

            option = cls._parse_linux_option(price, name, info[i], urls[i], storage[i])
            yield option

    @staticmethod
    def _parse_linux_option(price, name, info, url, storage):
        elements = str(info).split('<br/>')
        price = price.replace(',', '.')
        c = CurrencyConverter()

        option = VpsOption(
            name=str(name).strip(),
            storage=storage,
            cores=float((elements[0].split('>')[1].split(' CPU-Cores')[0]).strip()),
            memory=float((elements[2].split('GB Arbeitsspeicher')[0]).strip()),
            bandwidth='unmetered',
            connection=(int(elements[3].split('GB')[0]) * 1000),
            price=round(c.convert(price, 'EUR', 'USD'), 2),
            purchase_url=str(url).strip(),
        )
        return option

    @classmethod
    def _get_hrefs(cls):
        browser = cls._create_browser()
        browser.open("https://panel.linevast.de/cart.php")
        page = browser.get_current_page()
        hrefs = page.find_all('a', {'class': 'order-button'})

        lst = [None] * len(hrefs)

        for x in range(0, len(hrefs)):
            hrefs[x] = re.sub(r'[^\x00-\x7F]+','',str(hrefs)).decode('utf-8','ignore').strip()
            urlstring = str(hrefs[x]).split('href="')[1].split('"')[0]
            urlstring = urlstring.replace('/cart.php', '').replace('amp;', '')
            url = browser.get_url()
            url = url.split('?')[0]
            url = url + urlstring
            lst[x] = url

        return lst

    @classmethod
    def _get_storage(cls):
        browser = cls._create_browser()
        browser.open("https://panel.linevast.de/cart.php")
        page = browser.get_current_page()

        storage = [None] * 4

        for x in range(0, 4):
            storagetemp = page.find('li', {'id': 'product' + str(x+1) +'-feature3'})
            storagetemp = str(storagetemp).split('>')[1].split('GB')[0]
            storage[x] = int(storagetemp)

        return storage

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

    '''
    Control panel actions
    '''
    def enable_tun_tap(self):
        self._create_controlpanel()
        return self._controlpanel.enable_tun_tap()

    def change_root_password(self, new_password):
        self._create_controlpanel()
        return self._controlpanel.change_root_password(new_password)

    def get_status_control_panel(self):
        self._create_controlpanel()
        return self._controlpanel.get_status()


class LineVastClientArea(ClientArea):
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
            if title == 'New Server Information':
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

        tds = iter(soup.findAll('td'))
        while True:
            try:
                tdcontent = tds.next().renderContents().strip().decode('utf-8')
                if tdcontent == 'IP-Address:' and not server_info['ip_address']:
                    server_info['ip_address'] = tds.next().renderContents().strip().decode('utf-8')
                elif tdcontent == 'User:' and not server_info['server_user']:
                    server_info['server_user'] = tds.next().renderContents().strip().decode('utf-8')
                elif tdcontent == 'Password:' and not server_info['server_password']:
                    server_info['server_password'] = tds.next().renderContents().strip().decode('utf-8')
                elif tdcontent == 'Link:' and not server_info['control_panel_url']:
                    server_info['control_panel_url'] = tds.next().renderContents().strip().decode('utf-8')
                elif tdcontent == 'User:' and not server_info['vmuser']:
                    server_info['vmuser'] = tds.next().renderContents().strip().decode('utf-8')
                elif tdcontent == 'Password:' and not  server_info['vmuser_password']:
                    server_info['vmuser_password'] = tds.next().renderContents().strip().decode('utf-8')
            except StopIteration:
                break

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


class ControlPanel(object):
    """
    Control panel is allows the user to configure more advanced settings, such as TUN/TAP, rootpassword, hostname, etc.
    """

    _vi = None

    _valid_acts = set(['istun', 'rootpassword'])

    def __init__(self, browser, control_panel_url, vmuser, vmuser_password):
        self._browser = browser
        self._url = control_panel_url
        self._login(vmuser, vmuser_password)
        # self._enter_management()
        self._get_vi()

    def _login(self, user, password):
        """
        Login into the clientarea. Exits program if unsuccesful.
        :return: The clientarea homepage on succesful login.
        """
        self._browser.open(self._url)
        self._browser.select_form('form')
        self._browser['username'] = user
        self._browser['password'] = password
        page = self._browser.submit_selected()
        if "incorrect=true" in page.url:
            print("Login failure")
            sys.exit(2)

    def _get_vi(self):
        """
        The verification id needed for making POSTS to the control panel server.
        The purchased vm is first selected for management, from there the 'vi' can be parsed from source.
        :return: vi - verification id.
        """
        if not self._vi:
            self._browser.open(self._url)
            soup = self._browser.get_current_page()
            pattern = re.compile(r'control\.php\?_v=(.+)')
            ahref = soup.findAll('a', href=pattern)[0]['href']
            self._browser.open(self._url + '/' + ahref)
            msoup = self._browser.get_current_page()
            mpattern = re.compile(r'vi:\s*"(.+?)"')
            self._vi = mpattern.search(str(msoup)).group(1)
            print(self._vi)
        return self._vi

    def get_status(self):
        """
        Requests the status of the server
        :return: server status in json
        """
        res = self._browser.session.post(self._url+'/_vm_remote.php', data={'act': 'getstats', 'vi': self._get_vi()})
        return res.json()

    def _change_setting(self, act=None, opt=None):
        """
        Changes the a server setting, see _valid_acts for possible settings.
        :param act: setting/action
        :param opt: the new value. For binary (true/false, on/off) settings, use integers 1/0. Otherwise, string.
        :return: True if the setting was successfully changed. Else false.
        """
        if act not in self._valid_acts:
            raise ValueError("Setting action not found, available: [%s]" % ', '.join(self._valid_acts))

        data = {
            'act': act,
            'opt': opt,
            'vi': self._get_vi()
        }
        print("posting to: %s"%self._url + '/_vm_remote.php')
        res = self._browser.session.post(self._url + '/_vm_remote.php', data=data, verify=True)
        return res.status_code == 200

    def enable_tun_tap(self):
        print("Enabling TUN/TAP")
        return self._change_setting('istun', 1)

    def change_root_password(self, new_password):
        print("Changing password to: " + new_password)
        return self._change_setting('rootpassword', new_password)
