import json
import os
import unittest
import urllib.error
import urllib.parse
import urllib.request

from unittest.mock import patch, Mock

import requests

from cloudomate.gateway import coinbase, bitpay
from cloudomate.util.bitcoinaddress import validate


class TestCoinbase(unittest.TestCase):
    # test url from https://developers.coinbase.com/docs/merchants/payment-pages
    TEST_URL = 'https://www.coinbase.com/checkouts/2b30a03995ec62f15bdc54e8428caa87'
    amount = None
    address = None

    @classmethod
    def setUpClass(cls):
        cls.amount, cls.address = coinbase.extract_info(cls.TEST_URL)

    def test_address(self):
        self.assertTrue(validate(self.address))

    def test_amount(self):
        self.assertGreater(self.amount, 0)


class TestBitPay(unittest.TestCase):
    amount = None
    address = None
    rate = None

    @classmethod
    def setUpClass(cls):
        html_file = open(os.path.join(os.path.dirname(__file__), 'resources/bitpay_invoice_data.json'), 'r')
        data = html_file.read().encode('utf-8')
        response = requests.Response()
        response.read = Mock(return_value=data)
        with patch.object(urllib.request, 'urlopen', return_value=response):
            cls.amount, cls.address = bitpay.extract_info('https://bitpay.com/invoice?id=KXnWTnNsNUrHK2PEp8TpDC')

    def test_address(self):
        self.assertEqual(self.address, '12cWmVndhmD56dzYcRuYka3Vpgjb3qdRoL')
        pass

    def test_amount(self):
        self.assertEqual(self.amount, 0.001402)

    def test_address_valid(self):
        self.assertTrue(validate(self.address))
