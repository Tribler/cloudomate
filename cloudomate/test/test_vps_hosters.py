from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import unittest

from future import standard_library
from mock.mock import MagicMock
from parameterized import parameterized

from cloudomate.exceptions.vps_out_of_stock import VPSOutOfStockException
from cloudomate.hoster.vps.blueangelhost import BlueAngelHost
from cloudomate.hoster.vps.ccihosting import CCIHosting
from cloudomate.hoster.vps.crowncloud import CrownCloud
from cloudomate.hoster.vps.linevast import LineVast
from cloudomate.hoster.vps.pulseservers import Pulseservers
from cloudomate.hoster.vps.undergroundprivate import UndergroundPrivate
from cloudomate.util.fakeuserscraper import UserScraper
from cloudomate.util.settings import Settings

standard_library.install_aliases()

providers = [
    (LineVast,),  # TODO: Find out why the integration test for this one is unstable
    (BlueAngelHost,),
    (CCIHosting,),
    (CrownCloud,),
    (Pulseservers,),
    (UndergroundPrivate,),
]


class TestHosters(unittest.TestCase):
    @parameterized.expand(providers)
    def test_hoster_options(self, hoster):
        options = hoster.get_options()
        self.assertTrue(len(options) > 0)

    @parameterized.expand(providers)
    @unittest.skipIf(len(sys.argv) >= 2 and sys.argv[1] == 'discover', 'Integration tests have to be run manually')
    def test_hoster_purchase(self, hoster):
        user_settings = Settings()
        self._merge_random_user_data(user_settings)

        host = hoster(user_settings)
        options = list(host.get_options())[0]
        wallet = MagicMock()
        wallet.pay = MagicMock()

        try:
            host.purchase(wallet, options)
            wallet.pay.assert_called_once()
        except VPSOutOfStockException as exception:
            self.skipTest(exception)

    @staticmethod
    def _merge_random_user_data(user_settings):
        usergenerator = UserScraper()
        randomuser = usergenerator.get_user()
        for section in randomuser.keys():
            for key in randomuser[section].keys():
                user_settings.put(section, key, randomuser[section][key])


if __name__ == '__main__':
    unittest.main()
