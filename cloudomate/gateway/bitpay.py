from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

from future import standard_library
from future.moves.urllib import request

from cloudomate.gateway.gateway import Gateway, PaymentInfo

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
        bitpay_id = url.split("=")[1]
        url = "https://bitpay.com/invoices/" + bitpay_id
        response = request.urlopen(url)
        response_json = json.loads(response.read().decode('utf-8'))
        amount = float(response_json['data']['btcDue'])
        address = response_json['data']['bitcoinAddress']
        return PaymentInfo(amount, address)

    @staticmethod
    def get_gateway_fee():
        """Get the BitPay gateway fee.

        See: https://bitpay.com/pricing

        :return: The BitPay gateway fee
        """
        return 0.01
