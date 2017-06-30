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

from cloudomate import wallet as wallet_util

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
    gateway = None

    def __init__(self):
        """
        Initialize hoster object common variables
         configurations holds the vps options available
         br holds the stateful mechanize browser
        """
        self.configurations = None
        self.br = self._create_browser()

    def options(self):
        """
        Retrieve hosting options at Hoster.
        :return: A list of hosting options
        """
        options = self.start()
        self.configurations = list(options)
        return self.configurations

    def start(self):
        raise NotImplementedError('Abstract method implementation')

    def purchase(self, user_settings, vps_option, wallet):
        """
        Purchase a VPS
        :param wallet: bitcoin wallet
        :param user_settings: settings
        :param vps_option: server configuration
        :return: 
        """
        print('Purchasing %s instance: %s' % (type(self).__name__, vps_option.name))
        amount, address = self.register(user_settings, vps_option)
        print('Paying %s BTC to %s' % (amount, address))
        fee = wallet_util.get_network_fee()
        print('Calculated fee: %s' % fee)
        transaction_hash = wallet.pay(address, amount, fee)
        print('Done purchasing')
        return transaction_hash

    def register(self, user_settings, vps_option):
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

    def info(self, user_settings):
        """
        Get information for the last purchased service of specified provider.
        :param user_settings: the user settings including root password and login data.
        :return: 
        """
        raise NotImplementedError('Abstract method implementation')

    def print_configurations(self):
        """
        Print parsed VPS configurations.
        """
        row_format = "{:<5}" + "{:18}" * 8
        print(row_format.format("#", "Name", "CPU (cores)", "RAM (GB)", "Storage (GB)", "Bandwidth (TB)",
                                "Connection (Mbps)",
                                "Est. Price (mBTC)", "Price"))

        for i, item, estimated_price, price_string in self.get_configurations():
            print(row_format.format(i, item.name, str(item.cpu), str(item.ram), str(item.storage), str(item.bandwidth),
                                    str(item.connection), price_string, '{0} {1}'.format(item.currency, item.price)))

    def get_configurations(self):
        currencies = set(item.currency for item in self.configurations)
        rates = wallet_util.get_rates(currencies)
        transaction_fee = wallet_util.get_network_fee()
        for i, item in enumerate(self.configurations):
            if item.currency is not None:
                item_price = self.gateway.estimate_price(item.price * rates[item.currency])
                estimated_price = item_price + transaction_fee
                price_string = str(round(1000 * estimated_price, 2))
            else:
                price_string = 'est. unavailable'
            yield i, item, estimated_price, price_string

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
