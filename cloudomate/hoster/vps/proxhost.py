from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools
import json
from builtins import super

import ssl
import requests
import dateutil.parser
from mechanicalsoup import StatefulBrowser
from fake_useragent import UserAgent

from future import standard_library
from future.moves.urllib import request

from cloudomate.gateway.bitpay import BitPay
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.vps_hoster import VpsOption

standard_library.install_aliases()
from collections import namedtuple
from cloudomate.globals import __BASE_URL__

VpsConfiguration = namedtuple('VpsConfiguration', ['ip', 'root_password'])
VpsStatusResource = namedtuple('VpsStatusResource', ['used', 'total'])
VpsStatusResourceNone = VpsStatusResource(-1, -1)
VpsStatus = namedtuple('VpsStatus', ['memory',  # Memory VpsStatusResource in GB
                                     'storage',  # Storage VpsStatusResource in GB
                                     'bandwidth',  # Bandwidth VpsStatusResource in GB
                                     'online',  # Boolean
                                     'expiration',  # Python Datetime object
                                     'clientarea'])  # Service info retrieved from the ClientArea (for overriding)


class ProxHost(SolusvmHoster):
    # true if you can enable tuntap in the control panel
    TUN_TAP_SETTINGS = True

    BASE_URL = __BASE_URL__

    def __init__(self, settings):
        super(ProxHost, self).__init__(settings)

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_clientarea_url():
        return ''

    @staticmethod
    def get_gateway():
        return BitPay

    @staticmethod
    def get_metadata():
        return 'proxhost', 'https://codesalad.nl:5000/'

    @staticmethod
    def get_required_settings():
        return {
            'user': ['firstname', 'lastname', 'email', 'phonenumber', 'password'],
            'address': ['address', 'city', 'state', 'zipcode'],
        }

    def json_user_config(self):
        data = {
            'firstname': self._settings.get('user', "firstname"),
            'lastname': self._settings.get('user', "lastname"),
            'username': self._settings.get('user', "username"),
            'email': self._change_email_provider(self._settings.get('user', "email"), '@gmail.com'),
            'phonenumber': self._settings.get('user', "phonenumber"),
            'companyname': self._settings.get('user', "companyname"),
            'address1': self._settings.get('address', "address"),
            'city': self._settings.get('address', "city"),
            'state': self._settings.get('address', "state"),
            'postcode': self._settings.get('address', "zipcode"),
            'country': self._settings.get('address', 'countrycode'),
            'password': self._settings.get('user', "password"),
            'password2': self._settings.get('user', "password")
        }
        return data

    '''
    Action methods of the Hoster that can be called
    '''

    @classmethod
    def get_options(cls):
        """
        Linux (OpenVZ) and Windows (KVM) pages are slightly different, therefore their pages are parsed by different
        methods. Windows configurations allow a selection of Linux distributions, but not vice-versa.
        :return: possible configurations.
        """
        context = ssl._create_unverified_context()
        url = ProxHost.BASE_URL + '/options'
        response = request.urlopen(url, context=context)
        response_json = json.loads(response.read().decode('utf-8'))

        options = []
        for joption in response_json:
            options.append(VpsOption(
                name=joption['name'],
                storage=joption['storage'],
                cores=joption['cores'],
                memory=joption['memory'],
                bandwidth='unmetered',
                connection=joption['connection'],
                price=joption['price'],
                purchase_url=str(joption['vmid'])
            ))

        return list(options)

    def get_configuration(self):
        res = requests.post(self.BASE_URL+'/getconfiguration', json=self.json_user_config(), verify=False)
        print(res.content)
        config = json.loads(res.content)
        return VpsConfiguration(config['ip'], config['root_password'])

    def get_status(self):
        res = requests.post(self.BASE_URL+'/getstatus', json=self.json_user_config(), verify=False)
        print(res.content)
        status = json.loads(res.content.decode('utf8'))
        return VpsStatus(
            VpsStatusResourceNone,
            VpsStatusResourceNone,
            VpsStatusResourceNone,
            status['online'],  # online
            dateutil.parser.parse(status['expiration']),
            VpsStatusResourceNone
        )

    def purchase(self, wallet, option):
        data = self.json_user_config()
        res = requests.post(self.BASE_URL+'/purchase/'+option.purchase_url, json=self.json_user_config(), verify=False)
        print(res)
        pay_url = res.content.decode('utf8')
        print(pay_url)
        return self.pay(wallet, self.get_gateway(), pay_url)


    @staticmethod
    def get_ip(user_settings):
        res = requests.post(ProxHost.BASE_URL + '/getconfiguration', json=ProxHost(user_settings).json_user_config(), verify=False)
        print(res.content)
        config = json.loads(res.content)
        return config['ip']

    @staticmethod
    def _check_login(text):
        data = json.loads(text)
        if data['success'] and data['success'] == '1':
            return True
        return False
