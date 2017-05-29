"""
Hoster provides abstract implementations for common functionality
At this time there is no abstract implementation for any functionality.
"""
import os
import random
import webbrowser
from tempfile import mkstemp
from urlparse import urlparse

from mechanize import Browser
from forex_python.bitcoin import BtcConverter
from cloudomate import wallet

from cloudomate.vps.clientarea import ClientArea

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:53.0) Gecko/20100101 Firefox/53.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:53.0) Gecko/20100101 Firefox/53.0",
]


class Hoster(object):
    name = None
    website = None
    required_settings = None
    configurations = None
    client_area = None

    def options(self):
        """
        List the available VPS options for specified provider.
        :return: 
        """
        raise NotImplementedError('Abstract method implementation')

    def purchase(self, user_settings, vps_option):
        """
        Purchase an instance of specified provider.
        :param user_settings: the user settings used for registration.
        :param vps_option: the vps option to purchase.
        :return: 
        """
        raise NotImplementedError('Abstract method implementation')

    def get_status(self, user_settings):
        """
        Get the status of purchased services for specified provider.
        :param user_settings: the user settings used to login.
        :return: 
        """
        raise NotImplementedError('Abstract method implementation')

    def set_rootpw(self, user_settings):
        """
        Set the root password for the last purchased service of specified provider.
        :param user_settings: the user settings including root password and login data.
        :return: 
        """
        raise NotImplementedError('Abstract method implementation')

    def get_ip(self, user_settings):
        """
        Get the ip for the last purchased service of specified provider.
        :param user_settings: the user settings including root password and login data.
        :return: 
        """
        raise NotImplementedError('Abstract method implementation')

    def print_configurations(self):
        """
        Print parsed VPS configurations.
        """
        rate = wallet.Wallet().getrate()
        fee = wallet.Wallet().getfullfee()

        row_format = "{:<5}" + "{:18}" * 7
        print(row_format.format("#", "Name", "CPU (cores)", "RAM (GB)", "Storage (GB)", "Bandwidth (TB)", "Connection (Mbps)", "Estimated Price (mBTC)"))

        i = 0
        for item in self.configurations:
            print(row_format.format(i, item.name, item.cpu, item.ram, item.storage, item.bandwidth,
                                    item.connection, str( round(( (float(item.price) * rate) + fee)*1000, 2))))
            i = i + 1

    @staticmethod
    def _print_row(i, item, item_names):
        row_format = "{:<5}" + "{:15}" * len(item_names)
        values = [i]
        for key in item_names.keys():
            if key in item:
                values.append(item[key])
            else:
                values.append("")
        print(row_format.format(*values))

    @staticmethod
    def _create_browser():
        br = Browser()
        br.set_handle_robots(False)
        br.addheaders = [('User-agent', random.choice(user_agents))]
        return br

    @staticmethod
    def _open_in_browser(page):
        html = page.get_data()
        url = urlparse(page.geturl())
        html = html.replace('href="/', 'href="' + url.scheme + '://' + url.netloc + '/')
        html = html.replace('src="/', 'href="' + url.scheme + '://' + url.netloc + '/')
        fd, path = mkstemp()

        with open(path, 'w') as f:
            f.write(html)

        os.close(fd)

        webbrowser.open(path)

    def _clientarea_set_rootpw(self, user_settings, clientarea_url):
        email = user_settings.get('email')
        password = user_settings.get('password')
        clientarea = ClientArea(self._create_browser(), clientarea_url, email, password)
        rootpw = user_settings.get('rootpw')
        if 'number' in user_settings.config:
            clientarea.set_rootpw(rootpw, int(user_settings.get('number')))
        else:
            clientarea.set_rootpw(rootpw)

    def _clientarea_get_status(self, user_settings, clientarea_url):
        email = user_settings.get('email')
        password = user_settings.get('password')
        clientarea = ClientArea(self._create_browser(), clientarea_url, email, password)
        clientarea.print_services()

    def _clientarea_get_ip(self, user_settings, clientarea_url, client_data_url):
        email = user_settings.get('email')
        password = user_settings.get('password')
        clientarea = ClientArea(self._create_browser(), clientarea_url, email, password)
        if 'number' in user_settings.config:
            clientarea.get_ip(client_data_url, int(user_settings.get('number')))
        else:
            clientarea.get_ip(client_data_url)
