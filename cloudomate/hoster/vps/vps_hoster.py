from cloudomate import wallet as wallet_util

from cloudomate.hoster.hoster import Hoster


class VpsHoster(Hoster):
    required_settings = None
    configurations = None
    client_area = None

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

    def purchase(self, user_settings, options, wallet):
        """
        Purchase a VPS
        :param wallet: bitcoin wallet
        :param user_settings: settings
        :param options: server configuration
        :return:
        """
        print(('Purchasing %s instance: %s' % (type(self).__name__, options.name)))
        amount, address = self.register(user_settings, options)
        print(('Paying %s BTC to %s' % (amount, address)))
        fee = wallet_util.get_network_fee()
        print(('Calculated fee: %s' % fee))
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
        print((row_format.format("#", "Name", "CPU (cores)", "RAM (GB)", "Storage (GB)", "Bandwidth (TB)",
                                 "Connection (Mbps)",
                                 "Est. Price (mBTC)", "Price")))

        for i, item, estimated_price, price_string in self.get_configurations():
            print((row_format.format(i, item.name, str(item.cpu), str(item.ram), str(item.storage), str(item.bandwidth),
                                     str(item.connection), price_string, '{0} {1}'.format(item.currency, item.price))))

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
