from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import random
import string
from builtins import object

from future import standard_library

from mechanicalsoup import StatefulBrowser

standard_library.install_aliases()


class UserScraper(object):
    """
    Scrapes fakeaddressgenerator.com for fake user data.
    It also adds some basic additional information for server configuration.
    """

    attributes = [
        'Full Name',
        'Street',
        'City',
        'State Full',
        'Zip Code',
        'Phone Number',
        'Company',
        'Username'
    ]

    pages = {
        'NL': 'http://www.fakeaddressgenerator.com/World/Netherlands_address_generator',
        'US': 'http://www.fakeaddressgenerator.com/World/us_address_generator',
        'UK': 'http://www.fakeaddressgenerator.com/World/uk_address_generator',
        'CA': 'http://www.fakeaddressgenerator.com/World/ca_address_generator',
    }

    def __init__(self, country='NL'):
        self.country_code = country
        self.browser = StatefulBrowser()
        self.page = UserScraper.pages.get(country)

    def get_user(self):
        self.browser.open(self.page)
        attrs = {}

        for attr in self.attributes:
            attrs[attr] = self._get_attribute(attr)

        attrs['country_code'] = self.country_code
        attrs['password'] = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
        attrs['email'] = 'authentic8989+' + attrs['Username'] + '@gmail.com'
        attrs['rootpw'] = attrs['password']
        attrs['ns1'] = 'ns1'
        attrs['ns2'] = 'ns2'
        attrs['hostname'] = attrs['Username'] + '.hostname.com'
        attrs['testnet'] = 'off'

        return self._map_to_config(attrs)

    @staticmethod
    def _map_to_config(attrs):
        config = {}
        # Treat full name separately because it needs to be split
        if 'Full Name' in attrs:
            config['user'] = {}
            config['user']['firstname'] = attrs['Full Name'].split('\xa0')[0]
            config['user']['lastname'] = attrs['Full Name'].split('\xa0')[-1]

        # Map the possible user attributes to their config names and sections
        mapping = {
            'Street': ('address', 'address'),
            'City': ('address', 'city'),
            'State Full': ('address', 'state'),
            'Zip Code': ('address', 'zipcode'),
            'Phone Number': ('user', 'phonenumber'),
            'Company': ('user', 'companyname'),
            'Username': ('user', 'username'),
            'country_code': ('address', 'countrycode'),
            'password': ('user', 'password'),
            'email': ('user', 'email'),
            'rootpw': ('server', 'root_password'),
            'ns1': ('server', 'ns1'),
            'ns2': ('server', 'ns2'),
            'hostname': ('server', 'hostname'),
            'testnet': ('user', 'testnet')
        }

        for attr in attrs.keys():
            if attr in mapping.keys():
                section, key = mapping[attr]
                if section not in config:
                    config[section] = {}
                config[section][key] = attrs[attr]
        return config

    def _get_attribute(self, attribute):
        return self.browser.get_current_page() \
            .find(string=attribute) \
            .parent.parent.parent \
            .find('input') \
            .get('value')
