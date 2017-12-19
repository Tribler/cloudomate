import unittest

from parameterized import parameterized
from mock.mock import MagicMock

from cloudomate.exceptions.vps_out_of_stock import VPSOutOfStockException
from cloudomate.hoster.vps.blueangelhost import BlueAngelHost
from cloudomate.hoster.vps.ccihosting import CCIHosting
from cloudomate.hoster.vps.crowncloud import CrownCloud
from cloudomate.hoster.vps.legionbox import LegionBox
from cloudomate.hoster.vps.linevast import LineVast
from cloudomate.hoster.vps.pulseservers import Pulseservers
from cloudomate.hoster.vps.undergroundprivate import UndergroundPrivate

from cloudomate.util.fakeuserscraper import UserScraper

providers = [
    (LineVast,),
    (BlueAngelHost,),
    (CCIHosting,),
    (CrownCloud,),
    (LegionBox,),
    (Pulseservers,),
    (UndergroundPrivate,),
]


class TestHosters(unittest.TestCase):
    @parameterized.expand(providers)
    def test_hoster_options(self, hoster):
        options = hoster().start()
        self.assertTrue(len(list(options)) > 0)

    @parameterized.expand(providers)
    def test_hoster_purchase(self, hoster):
        user_settings = UserScraper().get_user()
        host = hoster()
        options = list(host.start())[0]
        wallet = MagicMock()
        wallet.pay = MagicMock()

        try:
            host.purchase(user_settings, options, wallet)
            wallet.pay.assert_called_once()
        except VPSOutOfStockException as exception:
            self.skipTest(exception)


if __name__ == '__main__':
    unittest.main()
