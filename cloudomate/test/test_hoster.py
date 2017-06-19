import unittest

from cloudomate.vps.legionbox import LegionBox
from mock.mock import MagicMock
from parameterized import parameterized

import cloudomate.vps.hoster
from cloudomate import wallet
from cloudomate.vps.blueangelhost import BlueAngelHost
from cloudomate.vps.ccihosting import CCIHosting
from cloudomate.vps.crowncloud import CrownCloud
from cloudomate.vps.linevast import LineVast
from cloudomate.vps.pulseservers import Pulseservers
from cloudomate.vps.rockhoster import RockHoster
from cloudomate.vps.undergroundprivate import UndergroundPrivate
from cloudomate.vps.vpsoption import VpsOption

providers = [
    (RockHoster,),
    (Pulseservers,),
    (CCIHosting,),
    (CrownCloud,),
    (BlueAngelHost,),
    (LineVast,),
    (LegionBox,),
    (UndergroundPrivate,),
]


class TestHosters(unittest.TestCase):
    @parameterized.expand(providers)
    def test_hoster_implements_interface(self, hoster):
        self.assertTrue('options' in dir(hoster), msg='options is not implemented in {0}'.format(hoster.name))
        self.assertTrue('purchase' in dir(hoster), msg='purchase is not implemented in {0}'.format(hoster.name))

    @parameterized.expand(providers)
    def test_hoster_options(self, hoster):
        options = hoster().start()
        self.assertTrue(len(list(options)) > 0)


class TestHosterAbstract(unittest.TestCase):
    def test_hoster_options(self):
        hoster = cloudomate.vps.hoster.Hoster()
        self.assertRaises(NotImplementedError, hoster.options)

    def test_hoster_purchase(self):
        hoster = cloudomate.vps.hoster.Hoster()
        vps_option = VpsOption(name='', price='', cpu='', currency='USD', ram='', storage='', bandwidth='',
                               connection='', purchase_url='')
        self.assertRaises(NotImplementedError, hoster.purchase, *(None, vps_option, None))

    def test_hoster_print(self):
        hoster = cloudomate.vps.hoster.Hoster()
        options = [self._create_option()]
        hoster.configurations = options
        wallet.get_rates = MagicMock(return_value={'USD': 1.1})
        hoster.gateway = MagicMock()
        hoster.gateway.estimate_price.return_value = 1.2
        hoster.print_configurations()
        wallet.get_rates.assert_called_once()
        hoster.gateway.estimate_price.assert_called_once()

    def test_create_browser(self):
        hoster = cloudomate.vps.hoster.Hoster()
        browser = hoster._create_browser()
        for header in browser.addheaders:
            if 'Mozilla/5.0' in header[1]:
                return True
        self.fail('No User-agent set in browser')

    @staticmethod
    def _create_option():
        return VpsOption(
            name="Option name",
            ram="Option ram",
            cpu="Option cpu",
            storage="Option storage",
            bandwidth="Option bandwidth",
            price=12,
            currency="USD",
            connection="Option connection",
            purchase_url="Option url"
        )


if __name__ == '__main__':
    unittest.main()
