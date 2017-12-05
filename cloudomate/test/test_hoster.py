import unittest

import cloudomate.hoster.vps.vps_hoster
from cloudomate import wallet
from cloudomate.hoster.vps.blueangelhost import BlueAngelHost
from cloudomate.hoster.vps.ccihosting import CCIHosting
from cloudomate.hoster.vps.crowncloud import CrownCloud
from cloudomate.hoster.vps.legionbox import LegionBox
from cloudomate.hoster.vps.linevast import LineVast
from cloudomate.hoster.vps.pulseservers import Pulseservers
from cloudomate.hoster.vps.undergroundprivate import UndergroundPrivate
from cloudomate.hoster.vps.vpsoption import VpsOption
from mock.mock import MagicMock
from parameterized import parameterized

providers = [
    (BlueAngelHost,),
    (CCIHosting,),
    (CrownCloud,),
    (LegionBox,),
    (LineVast,),
    (Pulseservers,),
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
        hoster = cloudomate.hoster.vps.hoster.Hoster()
        self.assertRaises(NotImplementedError, hoster.options)

    def test_hoster_purchase(self):
        hoster = cloudomate.hoster.vps.hoster.Hoster()
        vps_option = VpsOption(name='', price='', cpu='', currency='USD', ram='', storage='', bandwidth='',
                               connection='', purchase_url='')
        self.assertRaises(NotImplementedError, hoster.purchase, *(None, vps_option, None))

    def test_hoster_print(self):
        hoster = cloudomate.hoster.vps.hoster.Hoster()
        options = [self._create_option()]
        hoster.configurations = options
        wallet.get_rates = MagicMock(return_value={'USD': 1.1})
        hoster.gateway = MagicMock()
        hoster.gateway.estimate_price.return_value = 1.2
        hoster.print_configurations()
        wallet.get_rates.assert_called_once()
        hoster.gateway.estimate_price.assert_called_once()

    def test_create_browser(self):
        hoster = cloudomate.hoster.vps.hoster.Hoster()
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
