from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re

from fake_useragent import UserAgent
from future import standard_library
from mechanicalsoup import StatefulBrowser

from cloudomate.gateway.gateway import Gateway, PaymentInfo

standard_library.install_aliases()


class Coinify(Gateway):

    @staticmethod
    def get_name():
        return "coinify"

    @staticmethod
    def extract_info(url):
        user_agent = UserAgent(fallback="Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0")
        browser = StatefulBrowser(user_agent=user_agent.random)
        browser.open(url)
        page = browser.get_current_page()
        result = re.search(r'"bitcoin:([\w\d]+)\?amount=(\d+\.\d+)&', str(page))
        return PaymentInfo(float(result.group(2)), result.group(1))
