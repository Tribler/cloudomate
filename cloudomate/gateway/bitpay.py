from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import os
from math import pow

from future import standard_library
from future.moves.urllib import request
from future.moves.urllib.parse import urlsplit, parse_qs

from cloudomate.gateway.gateway import Gateway, PaymentInfo
from cloudomate.util.settings import Settings
from cloudomate import globals

import electrum.bitcoin as bitcoin
from electrum import paymentrequest as pr

standard_library.install_aliases()


class BitPay(Gateway):
    @staticmethod
    def get_name():
        return "BitPay"

    @staticmethod
    def extract_info(url):
        """
        Extracts amount and BitCoin address from a BitPay URL.
        :param url: the BitPay URL like "https://bitpay.com/invoice?id=J3qU6XapEqevfSCW35zXXX"
        :return: a tuple of the amount in BitCoin along with the address
        """
        # https://bitpay.com/ or https://test.bitpay.com
        uspl = urlsplit(url)
        base_url = "{0.scheme}://{0.netloc}".format(uspl)
        print(base_url)
        invoice_id = uspl.query.split("=")[1]

        # On the browser, users have to select between Bitcoin and Bitcoin cash 
        # trigger bitcoin selection for successful transaction 
        trigger_url = "{}/invoice-noscript?id={}&buyerSelectedTransactionCurrency=BTC".format(base_url, invoice_id)
        print(trigger_url)
        request.urlopen(trigger_url)

        # Make the payment
        payment_url = "bitcoin:?r={}/i/{}".format(base_url, invoice_id)
        print(payment_url)

        # Check for testnet mode
        if os.getenv('TESTNET', '0') == '1' and uspl.netloc == 'test.bitpay.com':
            bitcoin.set_testnet()

        # get payment request using Electrum's lib
        pq = parse_qs(urlsplit(payment_url).query)
        out = {k: v[0] for k, v in pq.items()}
        payreq = pr.get_payment_request(out.get('r')).get_dict()

        # amount is in satoshis (1/10e8 Bitcoin)
        amount = float(payreq.get('amount')) / pow(10, 8)
        address = payreq.get('requestor')

        return PaymentInfo(amount, address)

    @staticmethod
    def get_gateway_fee():
        """Get the BitPay gateway fee.

        See: https://bitpay.com/pricing

        :return: The BitPay gateway fee
        """
        return 0.01
