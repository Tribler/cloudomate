from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest
import datetime
from unittest import mock

from future import standard_library
from mock.mock import MagicMock 

from cloudomate.hoster.vpn.mullvad import MullVad
from cloudomate.hoster.vpn.vpn_hoster import VpnOption
from cloudomate.util.settings import Settings
from cloudomate.wallet import Wallet

standard_library.install_aliases()


class TestMullvad(unittest.TestCase):
     
    def setUp(self):
        self.settings = Settings()
        self.settings.put("user", "accountnumber", "2132sadfqf")
        self.wallet = MagicMock(Wallet)
        self.mullvad = MullVad(self.settings)
        self.option = MagicMock(VpnOption)

    def test_purchase(self):
        self.mullvad._login = MagicMock()
        self.mullvad._order = MagicMock()
        self.mullvad.pay = MagicMock()
 
        self.mullvad.purchase(self.wallet, self.option)
        
        self.assertTrue(self.mullvad._login.called)
        self.assertTrue(self.mullvad._order.called)
        self.assertTrue(self.mullvad.pay.called)

    def test_get_status(self):
        self.mullvad._get_expiration_date = MagicMock(return_value="2 January 2019")
        self.mullvad._login = MagicMock()
        now = datetime.datetime.strptime("9 December 2018", "%d %B %Y")
        self.mullvad._get_current_date = MagicMock(return_value=now)

        (online, expire_date) = self.mullvad.get_status()

        self.assertEqual(True, online)
        self.assertEqual(2019, expire_date.year)
        self.assertEqual(1, expire_date.month)
        self.assertEqual(2, expire_date.day)


if __name__ == "__main__":
    unittest.main()
