from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from abc import abstractmethod
from collections import namedtuple

from future import standard_library

from cloudomate.hoster.hoster import Hoster

standard_library.install_aliases()

VpnConfiguration = namedtuple('VpnConfiguration', ['username', 'password', 'ovpn'])
VpnOption = namedtuple('VpnOption', ['name', 'protocol', 'price', 'bandwidth', 'speed'])  # Price in USD
VpnStatus = namedtuple('VpnStatus', ['online', 'expiration'])  # Online is a boolean, expiration an ISO datetime


class VpnHoster(Hoster):
    """
    Abstract class for VPN Hosters.
    This defines all required subclass methods and implements some common methods.
    """

    @abstractmethod
    def get_configuration(self):
        """Get Hoster configuration.

        :return: Returns VpnConfiguration for the VPN Hoster instance
        """
        pass

    @classmethod
    @abstractmethod
    def get_options(cls):
        """Get Hoster options.

        :return: Returns list of VpnOption objects
        """
        pass

    @abstractmethod
    def get_status(self):
        """Get Hoster configuration.

        :return: Returns VpnStatus of the VPN Hoster instance
        """
        pass
