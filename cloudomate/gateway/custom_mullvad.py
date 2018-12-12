from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

from future import standard_library
from future.moves.urllib import request

from cloudomate.gateway.gateway import Gateway, PaymentInfo

standard_library.install_aliases()


class CustomMullvad(Gateway):
    @staticmethod
    def get_name():
        return "CustomMullvad"

    @staticmethod
    def extract_info(page):
        """
        Extracts amount and BitCoin address from MullVad's payment page.
        :param page: the HTML page returned after sumbitting the order 
        :return: a tuple of the amount in BitCoin along with the address
        """
        month_price = ""
        bitcoin_address = ""
        
        # Parse page to get bitcoin ammount and address
        for line in page.split("\n"):
            if "1 month = " in line:
                month_price = float(line.strip().split(" ")[3])
            if "input readonly" in line:
                bitcoin_address_line = line.strip().split(" ")[3].split("=")[1]
                bitcoin_address = bitcoin_address_line.partition("\"")[-1]
                bitcoin_address = bitcoin_address.rpartition("\"")[0]
 
        return PaymentInfo(month_price, bitcoin_address)

    @staticmethod
    def get_gateway_fee():
        """Get the BitPay gateway fee.

        See: https://bitpay.com/pricing

        :return: The BitPay gateway fee
        """
        return 0.00
