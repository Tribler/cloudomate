import unittest

import cloudomate.hoster.vps.vps_hoster
from cloudomate.hoster.vps.vpsoption import VpsOption
from mock.mock import MagicMock
from cloudomate import wallet

class TestHosters(unittest.TestCase):

    def test_options(self):
        hoster = cloudomate.hoster.vps.vps_hoster.VpsHoster()
        options = [self._create_option()]
        hoster.start= MagicMock(return_value=options)
        hoster.options()
        self.assertEqual(hoster.options(),options)

    def test_hoster_start(self):
        hoster = cloudomate.hoster.vps.vps_hoster.VpsHoster()
        self.assertRaises(NotImplementedError, hoster.start)


    def test_hoster_print(self):
        hoster = cloudomate.hoster.vps.vps_hoster.VpsHoster()
        options = [self._create_option()]
        hoster.configurations = options
        wallet.get_rates = MagicMock(return_value={'USD': 1.1})
        hoster.gateway = MagicMock()
        hoster.gateway.estimate_price.return_value = 1.2
        hoster.print_configurations()
        wallet.get_rates.assert_called_once()
        hoster.gateway.estimate_price.assert_called_once()

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