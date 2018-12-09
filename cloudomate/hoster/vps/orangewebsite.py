from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import re
import sys
from builtins import round
from builtins import super

from currency_converter import CurrencyConverter
from future import standard_library
from mechanicalsoup.utils import LinkNotFoundError

from cloudomate.gateway.bitpay import BitPay
from cloudomate.hoster.vps.clientarea import ClientArea
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.vps_hoster import VpsOption

standard_library.install_aliases()


class OrangeWebsite(SolusvmHoster):
    CART_URL = 'https://secure.orangewebsite.com/cart.php?a=view'

    # true if you can enable tuntap in the control panel
    TUN_TAP_SETTINGS = True

    _settings = None
    _controlpanel = None

    def __init__(self, settings):
        super(OrangeWebsite, self).__init__(settings)

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_clientarea_url():
        return 'https://panel.linevast.de/clientarea.php'

    @staticmethod
    def get_email_url():
        return 'https://panel.linevast.de/viewemail.php'  # + ?id=123456

    @staticmethod
    def get_gateway():
        return BitPay

    @staticmethod
    def get_metadata():
        return 'orangewebsite', 'https://www.orangewebsite.com/'

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
        browser.open("https://www.orangewebsite.com/vps.php")
        options = cls._parse_openvz_hosting(browser.get_current_page())
        lst = list(options)

        return lst

    def purchase(self, wallet, option):
        self._browser.open(option.purchase_url)
        self._server_form()
        self._browser.open(self.CART_URL)
        self._cart_form()

        # self._browser.open("https://secure.orangewebsite.com/cart.php?a=checkout")
        # self._browser.session.headers['referer'] = "https://secure.orangewebsite.com/cart.php?a=view"
        # self._browser.open("https://secure.orangewebsite.com/cart.php?a=complete")

        # print(self._browser.get_current_page())
        print(self._browser.get_url())

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
        form = self._browser.select_form('form#orderfrm')

        form['configoption[6]'] = '1127'  # Ubuntu 16.04
        form.set("ajax", 1, force=True)

        # checkout = self._browser.get_current_page().find("input", {"value": "Checkout"})

        self._browser.submit_selected()

    def _cart_form(self):
        form = self._browser.select_form('form#mainfrm')

        form['email'] = self._change_email_provider(self._settings.get('user', "email"), '@gmail.com')
        form['password'] = self._settings.get('user', "password")
        form['password2'] = self._settings.get('user', "password")
        form['paymentmethod'] = 'bitpay'
        # form['cctype'] = 'visa'
        # form['ccexpirymonth'] = 01
        # form['ccexpiryyear'] = 2018

        form['accepttos'] = True

        # form.print_summary()

        response = self._browser.submit_selected()

        # print(response.text)


    @classmethod
    def _parse_openvz_hosting(cls, page):
        options = page.find_all('li', {'class': 'virtual'})
        for idx, option in enumerate(options, start=1):
            list_elements = option.find_all('span', {"class": "right"})
            price_eur = float(option.find('span', {'class', 'price_figure'}).text[1:])
            c = CurrencyConverter()
            price_usd = round(c.convert(price_eur, 'EUR', 'USD'), 2)
            yield VpsOption(
                name=option.find('h3').text.strip().replace("Virtual Server - ", ""),
                storage=list_elements[1].text.strip().split(' ')[0][:-2],
                cores=list_elements[2].text.strip().split(' ')[0],
                memory=float(list_elements[0].text.strip().split(' ')[0][:-2])/1024,
                bandwidth=list_elements[3].text.strip().split(' ')[0][:-2],
                connection=1,
                price=price_usd,
                purchase_url=option.find_all('a', {'class': 'action_button'})[1]['href'],
            )

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
                elif tdcontent == 'Password:' and not server_info['vmuser_password']:
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

    _valid_acts = {'istun', 'rootpassword'}

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
        res = self._browser.session.post(self._url + '/_vm_remote.php', data={'act': 'getstats', 'vi': self._get_vi()})
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
        print("posting to: %s" % self._url + '/_vm_remote.php')
        res = self._browser.session.post(self._url + '/_vm_remote.php', data=data, verify=True)
        return res.status_code == 200

    def enable_tun_tap(self):
        print("Enabling TUN/TAP")
        return self._change_setting('istun', 1)

    def change_root_password(self, new_password):
        print("Changing password to: " + new_password)
        return self._change_setting('rootpassword', new_password)
