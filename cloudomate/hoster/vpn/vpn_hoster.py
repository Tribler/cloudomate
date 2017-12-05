from cloudomate.hoster.hoster import Hoster
from collections import namedtuple
from cloudomate import wallet as wallet_util

import sys


VpnOptions = namedtuple('VpnOptions', ['name', 'protocol', 'price', 'bandwidth', 'speed'])
VpnStatus = namedtuple('VpnStatus', ['online', 'expiration'])
VpnInfo = namedtuple('VpnInfo', ['username', 'password', 'ovpn'])

class VpnHoster(Hoster):
    """
    Abstract class for VPN Hosters, concrete classes should provide the information in the __init__ function.
    """

    def __init__(self):
        super().__init__()

        self.name = None
        self.website = None
        self.protocol = None
        self.price = None
        self.bandwidth = None
        self.speed = None

    def info(self, user_settings):
        """
        This function should display information on the VPN service such as
        :return:
        """
        raise NotImplementedError('Abstract method implementation')

    def purchase(self, user_settings, wallet):
        """
        This function should actually buy a vps server with the specified wallet and provided credentials.
        """
        raise NotImplementedError('Abstract method implementation')

    def status(self, user_settings):
        """
        This function should provide the status of the last activated VPN subscription.
        """
        raise NotImplementedError('Abstract method implementation')

    def get_status(self, user_settings):
        # Backward compatibility, apparently this method should print and not return the values
        row = "{:18}" * 2
        status = self.status(user_settings)
        print(row.format("Online", "Expiration"))
        print(row.format(str(status.online), status.expiration.isoformat()))

    def options(self):
        return VpnOptions(self.name, self.protocol, self.price, self.bandwidth, self.speed)

    def print_options(self, options):
        bandwidth = "Unlimited" if options.bandwidth == sys.maxsize else options.bandwidth
        speed = "Unlimited" if options.speed == sys.maxsize else options.speed

        # Calculate the estimated price
        rate = wallet_util.get_rate("USD")
        fee = wallet_util.get_network_fee()
        estimate = self.gateway.estimate_price(options.price * rate) + fee  # BTC
        estimate = round(1000 * estimate, 2)  # mBTC

        # Print everything
        row = "{:18}" * 6
        print(row.format("Name", "Protocol", "Bandwidth", "Speed", "Est. Price (mBTC)", "Price (USD)"))
        print(row.format(options.name, options.protocol, bandwidth, speed, str(estimate), str(options.price)))

    # For compatibility with the commandline code
    def print_configurations(self):
        options = self.options()
        self.print_options(options)
