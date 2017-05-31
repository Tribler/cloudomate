# -*- coding: utf-8 -*-

import json
import subprocess
import time
from mechanize import Browser

from forex_python.bitcoin import BtcConverter


def determine_currency(text):
    """
    Determine currency of text
    :param text: text cointaining a currency symbol
    :return: currency name of symbol
    """
    if '$' in text or 'usd' in text.lower():
        return 'USD'
    elif u'€' in text or 'eur' in text.lower():
        return 'EUR'
    else:
        return None

AVG_TX_SIZE = 226
SATOSHI_TO_BTC = 0.00000001


def get_rate(currency='USD'):
    """
    Return price of 1 currency in BTC
    Supported currencies available at http://forex-python.readthedocs.io/en/latest/currencysource.html#list-of-supported-currency-codes
    :param currency: currency to convert to
    :return: conversion rate from currency to BTC
    """
    if currency is None:
        return None
    b = BtcConverter()
    factor = b.get_latest_price(currency)
    if factor is None:
        return None
    return 1.0 / factor

def get_rates(currencies):
    """
    Return rates for all currencies to BTC.
    :return: conversion rates from currencies to BTC
    """
    rates = {cur: get_rate(cur) for cur in currencies}
    return rates

def get_price(amount, currency='USD'):
    """
    Convert price from one currency to bitcoins
    :param amount: number of currencies to convert
    :param currency: currency to convert from
    :return: price in bitcoins
    """
    price = amount * get_rate(currency)
    return price

def _get_network_cost(speed):
    br = Browser()
    br.addheaders = [('User-Agent', 'Firefox')]
    page = br.open('https://bitcoinfees.21.co/api/v1/fees/recommended')
    rates = json.loads(page.read())
    satoshirate = float(rates[speed])
    return satoshirate

def get_network_fee(speed='halfHourFee'):
    """
    Give an estimate of network fee for the average bitcoin transaction for given speed.
    Supported speeds are available at https://bitcoinfees.21.co/api/v1/fees/recommended
    :return: network cost
    """
    network_fee = _get_network_cost(speed) * SATOSHI_TO_BTC
    return network_fee * AVG_TX_SIZE


class Wallet:
    """
    Wallet implements an adapter to the default electrum wallet.
    Currently Wallet only supports wallets without passwords for automated operation.
    Wallets with passwords may still be used, but passwords will have to be entered manually.
    """
    def __init__(self, wallet_command=['electrum']):
        self.command = wallet_command

    def get_balance(self, confirmed=True, unconfirmed=True):
        """
        Return the balance of the default electrum wallet
        Confirmed and unconfirmed can be set to indicate which balance to retrieve.
        :param confirmed: default: True
        :param unconfirmed: default: True
        :return: balance of default wallet
        """
        output = str(subprocess.check_output(self.command + ['getbalance']))
        balance_dict = json.loads(output)
        balance = 0.0
        if confirmed:
            balance = balance + float(balance_dict.get('confirmed', 0.0))
        if unconfirmed:
            balance = balance + float(balance_dict.get('unconfirmed', 0.0))
        return balance

    def get_balance_confirmed(self):
        """
        Return confirmed balance of default electrum wallet
        :return: 
        """
        return self.get_balance(confirmed=True, unconfirmed=False)

    def get_balance_unconfirmed(self):
        """
        Return unconfirmed balance of default electrum wallet
        :return: 
        """
        return self.get_balance(confirmed=False, unconfirmed=True)

    def get_addresses(self):
        """
        Return the list of addresses of the default electrum wallet
        :return: 
        """
        address = str(subprocess.check_output(self.command + ['listaddresses']))
        addr = json.loads(address)
        addresses = addr[0]
        return addresses

    def pay(self, address, amount, fee):
        with ElectrumWalletHandler(self.command) as wh:
            if self.getbalance() < amount + fee:
                print 'NotEnoughFunds'
            else:
                subprocess.check_output(wh.command + ['payto', str(address), str(amount), '-f', str(fee)])
                print 'payment succeeded'

    def pay_autofee(self, address, amount):
        with ElectrumWalletHandler(self.command) as wh:
            amount = amount + self.getfee() + self.getbitpayfee()
            if self.getbalance() < amount:
                print 'NotEnoughFunds'
            else:
                output = subprocess.check_output(wh.command + ['payto', str(address), str(amount)])
                temp = json.loads(output)
                hextransaction = temp['hex']
                subprocess.call(wh.command + ['broadcast', hextransaction])
                print 'payment succeeded'

    def empty_wallet(self, address):
        with ElectrumWalletHandler(self.command) as wh:
            if self.getbalance() is not 0.0:
                output = subprocess.check_output(wh.command + ['payto', address, '!'])
                temp = json.loads(output)
                hextransaction = temp['hex']
                subprocess.call(wh.command + ['broadcast', hextransaction])
                print 'Wallet was successfully emptied'
            else:
                print 'Wallet already empty'


class ElectrumWalletHandler(object):
    """
    ElectrumWalletHandler ensures the correct opening and closing of the electrum wallet daemon
    """
    def __init__(self, wallet_command=['electrum']):
        """
        Allows wallet_command to be changed to for example electrum --testnet
        :param wallet_command: command to call wallet
        """
        self.command = wallet_command

    def __enter__(self):
        # things that can go wrong, unable to start
        # other things
        subprocess.call(self.command + ['daemon', 'start'])
        subprocess.call(self.command + ['daemon', 'load_wallet'])

    def __exit__(self):
        time.sleep(5)
        subprocess.call(self.command + ['daemon', 'stop'])
