import unittest

import cloudomate.vps.hoster


class TestHoster(unittest.TestCase):
    def testHoster(self):
        hoster = cloudomate.vps.hoster.Hoster()
        self.assertRaises(NotImplementedError, hoster.options)


if __name__ == '__main__':
    unittest.main()
