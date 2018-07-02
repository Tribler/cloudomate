from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from unittest import TestCase
from unittest import skip
from builtins import open

from mock import patch, Mock

import requests
from future import standard_library
from future.moves.urllib import request

from cloudomate.gateway.bitpay import BitPay
from cloudomate.gateway.coinbase import Coinbase
from cloudomate.util.bitcoinaddress import validate

standard_library.install_aliases()


class TestCoinbase(TestCase):
    # TODO find a new test coinbase url the old one isn't used anymore
    # test url from https://developers.coinbase.com/docs/merchants/payment-pages
    TEST_URL = 'https://www.coinbase.com/checkouts/2b30a03995ec62f15bdc54e8428caa87'
    amount = None
    address = None

    @classmethod
    @skip('the TEST_URL isn\t used anymore needs a replacement url')
    def setUpClass(cls):
        cls.amount, cls.address = Coinbase.extract_info(cls.TEST_URL)

    def test_address(self):
        self.assertTrue(validate(self.address))

    def test_amount(self):
        self.assertGreater(self.amount, 0)


class TestBitPay(TestCase):
    amount = None
    address = None
    rate = None

    @classmethod
    @skip('the TEST_URL isn\t used anymore needs a replacement url')
    def setUpClass(cls):
        html_file = open(os.path.join(os.path.dirname(__file__), 'resources/bitpay_invoice_data.json'), 'r')
        data = html_file.read().encode('utf-8')
        html_file.close()
        response = requests.Response()
        response.read = Mock(return_value=data)
        with patch.object(request, 'urlopen', return_value=response):
            cls.amount, cls.address = BitPay.extract_info('https://bitpay.com/invoice?id=KXnWTnNsNUrHK2PEp8TpDC')

    def test_address(self):
        self.assertEqual(self.address, '12cWmVndhmD56dzYcRuYka3Vpgjb3qdRoL')
        pass

    def test_amount(self):
        self.assertEqual(self.amount, 0.001402)

    def test_address_valid(self):
        self.assertTrue(validate(self.address))
