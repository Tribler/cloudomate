from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from abc import abstractmethod
from collections import namedtuple

from future import standard_library

from cloudomate.hoster.hoster import Hoster

standard_library.install_aliases()

VpsConfiguration = namedtuple('VpsConfiguration', ['ip', 'root_password'])
VpsOption = namedtuple('VpsOption', ['name',
                                     'cores',
                                     'memory',  # Memory in GB
                                     'storage',  # Storage in GB
                                     'bandwidth',  # Bandwidth in GB
                                     'connection',  # Connection speed in Gbps
                                     'price',  # Price in USD
                                     'purchase_url'])
VpsStatusResource = namedtuple('VpsStatusResource', ['used', 'total'])
VpsStatusResourceNone = VpsStatusResource(-1, -1)
VpsStatus = namedtuple('VpsStatus', ['memory',  # Memory VpsStatusResource in GB
                                     'storage',  # Storage VpsStatusResource in GB
                                     'bandwidth',  # Bandwidth VpsStatusResource in GB
                                     'online',  # Boolean
                                     'expiration',  # Python Datetime object
                                     'clientarea'])  # Service info retrieved from the ClientArea (for overriding)


class VpsHoster(Hoster):
    """
    Abstract class for VPS Hosters.
    This class already implements some common methods.
    """


    @abstractmethod
    def get_configuration(self):
        """Get Hoster configuration.

        :return: Returns VpsConfiguration for the VPS Hoster instance
        """
        pass

    @classmethod
    @abstractmethod
    def get_options(cls):
        """Get Hoster options.

        :return: Returns list of VpsOption objects
        """
        pass

    @abstractmethod
    def get_status(self):
        """Get Hoster configuration.

        :return: Returns VpsStatus of the VPS Hoster instance
        """
        pass
