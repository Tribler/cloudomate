import unittest

from cloudomate.gateway import coinbase
from cloudomate.util.bitcoinaddress import validate
from cloudomate.wallet import get_rate


class TestCoinbase(unittest.TestCase):
    # test url from https://developers.coinbase.com/docs/merchants/payment-pages
    TEST_URL = 'https://www.coinbase.com/checkouts/2b30a03995ec62f15bdc54e8428caa87'
    amount = None
    address = None
    rate = None

    @classmethod
    def setUpClass(cls):
        cls.amount, cls.address = coinbase.extract_info(cls.TEST_URL)
        cls.rate = get_rate()

    def test_address(self):
        self.assertTrue(validate(self.address))

    def test_amount(self):
        # default donation is $1, so see if exchange rate is close
        self.assertTrue(0.99 * self.rate < self.amount < 1.01 * self.rate)
