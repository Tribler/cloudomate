from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from math import pow

import electrum.bitcoin as bitcoin
from electrum import paymentrequest as pr
from future import standard_library
from future.moves.urllib import request
from future.moves.urllib.parse import urlsplit, parse_qs

from cloudomate.gateway.gateway import Gateway, PaymentInfo
from cloudomate.hoster.hoster import Hoster

standard_library.install_aliases()


class CoinPayments(Gateway):

    @staticmethod
    def reuse_session():
        return True

    @staticmethod
    def get_name():
        return "CoinPayments"

    @staticmethod
    def extract_info(browser, settings):
        """
        Uses the browser to walk through the payment process of coinpayments
        :browser: a browser currently at https://www.coinpayments.net/index.php
        :settings: the usersettings to be given to coinpayments
        :return: a tuple of the amount in BitCoin along with the address
        """

        #select coin to pay
        browser.select_form(nr=0)
        form = browser.get_current_form()
        form['selcoin'] = 'BTC'
        form['checkout'] = 1
        form['first_name'] = settings.get('user', "firstname")
        form['last_name'] = settings.get('user', "lastname")
        form['email'] = settings.get('user', "email")
        form.set('screen_res', '1920x1080', force=True)
        response = browser.submit_selected()

        #go to actual payment page
        browser.open("https://www.coinpayments.net/index.php?cmd=checkout")
        page = browser.get_current_page()

        try:
            bitcoin_url = page.find('div', {'class': 'pay-block'}).find('a')['href']
        except AttributeError:
            print("Too many open transactions, try connecting from a different IP")
            raise

        dirty_address, dirty_amount = bitcoin_url.split("?")

        address = dirty_address.split(":")[1]
        amount = float(dirty_amount.split("=")[1])

        return PaymentInfo(amount, address)

    @staticmethod
    def get_gateway_fee():
        """Get the CoinPayments gateway fee.

        """
        return 0.00
