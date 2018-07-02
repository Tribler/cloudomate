# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import re
import sys
from builtins import round
from collections import namedtuple

from bs4 import BeautifulSoup
from forex_python.converter import CurrencyRates
from future import standard_library

standard_library.install_aliases()

ClientAreaService = namedtuple('ClientAreaService', ['name', 'price', 'next_due', 'status', 'url'])


class ClientArea(object):
    """
    Clientarea is the name of the control panel used in many VPS providers. The purpose of this class is to use
    this control panel in an automated manner.
    """
    ACTION_POSTFIX = '?action=services&language=english'

    def __init__(self, browser, clientarea_url, user_settings):
        self._browser = browser
        self._services = None
        self._url = clientarea_url
        self._login(user_settings.get('user', 'email'), user_settings.get('user', 'password'))

    def get_ip(self, service=None):
        if service is None:
            service = self.get_services_first()
        self._browser.open(service.url)
        soup = self._browser.get_current_page()
        rows = soup.select('div#domain > div.row')
        if len(rows) > 0:
            for row in rows:
                divs = row.findAll('div')
                if 'IP' in divs[0].strong.text:
                    return divs[1].text.strip()
        else:
            return re.search(r'\b((?:\d{1,3}\.){3}\d{1,3})\b', soup.text).group(0)

    def get_services(self):
        if self._services is None:
            self._browser.open(self._url + self.ACTION_POSTFIX)
            soup = self._browser.get_current_page()
            rows = soup.select('table#tableServicesList tbody tr')
            self._services = [self._parse_service_row(row) for row in rows]

        return self._services

    def get_services_first(self):
        return self.get_services()[0]

    def _parse_service_row(self, row):
        columns = row.findAll('td')

        name = columns[0].strong.text

        price_string = columns[1].text
        dot_index = price_string.index('.')
        price = float(price_string[1:dot_index + 3])

        next_due = columns[2].span.text
        next_due = datetime.datetime.strptime(next_due, '%Y-%m-%d')

        status = columns[3].span.text.lower()

        url = columns[4].a['href']
        url = url.split('.php')
        url = self._url + url[1]

        return ClientAreaService(name, price, next_due, status, url)

    def _login(self, email, password):
        """
        Login into the clientarea. Exits program if unsuccesful.
        :return: The clientarea homepage on succesful login.
        """
        self._browser.open(self._url)
        self._browser.select_form('.logincontainer form')
        self._browser['username'] = email
        self._browser['password'] = password
        page = self._browser.submit_selected()
        if "incorrect=true" in page.url:
            print("Login failure")
            sys.exit(2)
        self.home_page = page
