from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest
import datetime

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
        self.mullvad._check_vpn_date = MagicMock(return_value=(True,"-5"))
        self.mullvad._login = MagicMock()

        expiration_date = self.mullvad.get_status()[1]
        now = datetime.datetime.now(datetime.timezone.utc)
        expiration_days = datetime.timedelta(days=int("-5"))
        full_date = now + expiration_days

        self.assertEqual(expiration_date.day, full_date.day)
        self.assertEqual(expiration_date.month, full_date.month)


if __name__ == "__main__":
    unittest.main()
