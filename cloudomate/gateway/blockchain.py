from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from future import standard_library

from cloudomate.gateway.gateway import Gateway, PaymentInfo

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



