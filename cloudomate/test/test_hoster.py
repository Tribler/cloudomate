import unittest

from parameterized import parameterized

import cloudomate.vps.hoster
from cloudomate.vps.blueangelhost import BlueAngelHost
from cloudomate.vps.ccihosting import CCIHosting
from cloudomate.vps.crowncloud import CrownCloud
from cloudomate.vps.pulseservers import Pulseservers
from cloudomate.vps.rockhoster import RockHoster

providers = [
    (RockHoster,),
    (Pulseservers,),
    (CCIHosting,),
    (CrownCloud,),
    (BlueAngelHost,),
]


class TestHosters(unittest.TestCase):
    @parameterized.expand(providers)
    def testHosterImplementsInterface(self, hoster):
        self.assertTrue('options' in dir(hoster), msg='options is not implemented in {0}'.format(hoster.name))
        self.assertTrue('purchase' in dir(hoster), msg='purchase is not implemented in {0}'.format(hoster.name))


class TestHosterAbstract(unittest.TestCase):
    def testHosterOptions(self):
        hoster = cloudomate.vps.hoster.Hoster()
        self.assertRaises(NotImplementedError, hoster.options)

    def testHosterPurchase(self):
        hoster = cloudomate.vps.hoster.Hoster()
        self.assertRaises(NotImplementedError, hoster.purchase, *(None, None, None))


if __name__ == '__main__':
    unittest.main()
