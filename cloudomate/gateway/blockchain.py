from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
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


class Blockchain(Gateway):

    @staticmethod
    def get_name():
        return "blockchain"

    @staticmethod
    def extract_info(url):
      amount, address = str(url).split('&')
      am = float(amount)
      return PaymentInfo(am, address)



