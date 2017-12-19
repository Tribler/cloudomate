from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest

import os
from future import standard_library
from parameterized import parameterized

from cloudomate.hoster.vpn.azirevpn import AzireVpn
from cloudomate.util.settings import Settings

standard_library.install_aliases()

providers = [
    (AzireVpn,),
]


class TestHosters(unittest.TestCase):
    def setUp(self):
        self.settings = Settings()
        self.settings.read_settings(os.path.join(os.path.dirname(__file__), 'resources/test_settings.cfg'))

    @parameterized.expand(providers)
    def test_vpn_hoster_options(self, hoster):
        options = hoster.get_options()
        self.assertTrue(len(options) > 0)

    @parameterized.expand(providers)
    def test_vpn_hoster_configuration(self, hoster):
        config = hoster(self.settings).get_configuration()
        self.assertTrue(len(config) > 0)


if __name__ == '__main__':
    unittest.main()
