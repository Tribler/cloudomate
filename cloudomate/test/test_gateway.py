import unittest

from cloudomate.wallet import Wallet

from cloudomate.gateway import coinbase, bitpay

from bitcoinaddress.validation import validate

class TestCoinbase(unittest.TestCase):
    # test url from https://developers.coinbase.com/docs/merchants/payment-pages
    TEST_URL = 'https://www.coinbase.com/checkouts/2b30a03995ec62f15bdc54e8428caa87'

    def setUp(self):
        self.amount, self.address = coinbase.extract_info(self.TEST_URL)
        self.rate = Wallet().getrate()

    def test_address(self):
        self.assertTrue(validate(self.address))

    def test_amount(self):
        # default donation is $1, so see if exchange rate is close
        self.assertTrue(0.99 * self.rate < self.amount < 1.01 * self.rate)
