"""
Hoster provides abstract implementations for common functionality
At this time there is no abstract implementation for any functionality.
"""
import os
import random
import webbrowser
from mechanize import Browser
from tempfile import mkstemp
from urlparse import urlparse

from cloudomate import wallet

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

    def __init__(self):
        '''
        Initialize hoster object common variables
         configurations holds the vps options available
         br holds the stateful mechanize browser
        '''
        self.configurations = None
        self.br = self._create_browser()

    def options(self):
        '''
        Retrieve hosting options at Hoster.
        :return: A list of hosting options
        '''
        options = self.start()
        self.configurations = list(options)
        return self.configurations

    def start(self):
        raise NotImplementedError('Abstract method implementation')

    def purchase(self, user_settings, vps_option, wallet):
        '''
        Purchase a VPS
        :param user_settings: settings
        :param vps_option: server configuration
        :return: 
        '''
        print('Purchase')
        amount, address = self.register(user_settings, vps_option)

        # commented out so we don't accidentally buy servers
        # amount = float(amount)
        # fee = wallet.Wallet().getfee()
        # wallet.Wallet().pay(address, amount, fee)
        pass

    def register(self, user_settings, vps_option):
        raise NotImplementedError('Abstract method implementation')

    def print_configurations(self):
        """
        Print parsed VPS configurations.
        """
        rate = wallet.Wallet().getrate()
        fee = wallet.Wallet().getfullfee()

        row_format = "{:<5}" + "{:15}" * 7
        print(row_format.format("#", "Name", "CPU", "RAM", "Storage", "Bandwidth", "Connection", "Estimated Price"))

        i = 0
        for item in self.configurations:
            print(row_format.format(i, item.name, item.cpu, item.ram, item.storage, item.bandwidth,
                                    item.connection, str((float(item.price) * rate) + fee) + ' btc'))
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
