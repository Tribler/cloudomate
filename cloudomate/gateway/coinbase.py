from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys

from bs4 import BeautifulSoup
from future import standard_library

from cloudomate.gateway.gateway import Gateway, PaymentInfo

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import geckodriver_autoinstaller

standard_library.install_aliases()


class Coinbase(Gateway):
    @staticmethod
    def get_name():
        return "coinbase"

    @classmethod
    def extract_info(cls, url):
        """
        Extracts amount and BitCoin address from a Coinbase URL.
        :param url: the Coinbase URL like "https://commerce.coinbase.com/charges/K62GMV5Y"
        :return: a tuple of the amount in BitCoin along with the address
        """
        geckodriver_autoinstaller.install()  # Install the geckodriver of firefox if needed for selenium to work
        options = Options()
        options.headless = True  # don't show firefox window
        driver = webdriver.Firefox(options=options)

        driver.get(url)
        driver.implicitly_wait(20) # wait for the payment page to completely load
        driver.find_element_by_xpath('//img[@alt="Bitcoin"]').click()  # click on the bitcoin option
        address = cls._extract_address(driver)
        amount = cls._extract_amount(driver)
        driver.quit()

        return PaymentInfo(amount, address)

    @staticmethod
    def get_gateway_fee():
        """Get the coinbase gateway fee.

        See: https://support.coinbase.com/customer/portal/articles/1277919-what-fees-does-coinbase-charge-for-merchant-processing

        :return: The coinbase gateway fee
        """
        # I don't think there is any fee anymore
        return 0.01

    @staticmethod
    def _extract_amount(driver):
        """
        Extract amount from driver
        :param driver: webpage where the amount and address are stored
        :return: Amount to be transferred
        """
        return float(driver.find_elements_by_xpath('//div[contains(text(), "BTC")]')[1].text.split(' ')[0])

    @staticmethod
    def _extract_address(driver):
        """
        Extract address from driver
        :param driver: webpage where the amount and address are stored
        :return: Bitcoin address
        """
        return driver.find_element_by_id('payment-address').get_attribute('title')
