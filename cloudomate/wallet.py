# -*- coding: utf-8 -*-

import json
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request

from forex_python.bitcoin import BtcConverter
from mechanicalsoup import StatefulBrowser

AVG_TX_SIZE = 226
SATOSHI_TO_BTC = 0.00000001


def determine_currency(text):
    """
    Determine currency of text
    :param text: text cointaining a currency symbol
    :return: currency name of symbol
    """
    # Naive approach, for example NZ$ also contains $
    if '$' in text or 'usd' in text.lower():
        return 'USD'
    elif '€' in text or 'eur' in text.lower():
        return 'EUR'
    else:
        return None


def get_rate(currency='USD'):
    """
    Return price of 1 currency in BTC
    Supported currencies available at 
    http://forex-python.readthedocs.io/en/latest/currencysource.html#list-of-supported-currency-codes
    :param currency: currency to convert to
    :return: conversion rate from currency to BTC
    """
    if currency is None:
        return None
    b = BtcConverter()
    factor = b.get_latest_price(currency)
    if factor is None:
        factor = 1.0 / fallback_get_rate(currency)
    return 1.0 / factor


def fallback_get_rate(currency):
    # Sometimes the method above gets rate limited, in this case use
    # https: // blockchain.info / tobtc?currency = USD & value = 500
    return float(urllib.request.urlopen('https://blockchain.info/tobtc?currency={0}&value=1'.format(currency)).read())


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
    br = StatefulBrowser(user_agent='Firefox')
    page = br.open('https://bitcoinfees.21.co/api/v1/fees/recommended')
    response = page.json()
    satoshirate = float(response[speed])
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
    Wallet implements an adapter to the wallet handler.
    Currently Wallet only supports electrum wallets without passwords for automated operation.
    Wallets with passwords may still be used, but passwords will have to be entered manually.
    """

    def __init__(self, wallet_command=None, wallet_path=None):
        if wallet_command is None:
            if os.path.exists('/usr/local/bin/electrum'):
                wallet_command = ['/usr/local/bin/electrum']
            else:
                wallet_command = ['/usr/bin/env', 'electrum']
        self.command = wallet_command
        self.wallet_handler = ElectrumWalletHandler(wallet_command, wallet_path)

    def get_balance(self, confirmed=True, unconfirmed=True):
        """
        Return the balance of the default electrum wallet
        Confirmed and unconfirmed can be set to indicate which balance to retrieve.
        :param confirmed: default: True
        :param unconfirmed: default: True
        :return: balance of default wallet
        """
        balance_output = self.wallet_handler.get_balance()
        balance = 0.0
        if confirmed:
            balance = balance + float(balance_output.get('confirmed', 0.0))
        if unconfirmed:
            balance = balance + float(balance_output.get('unconfirmed', 0.0))
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
        address_output = self.wallet_handler.get_addresses()
        return address_output

    def pay(self, address, amount, fee=None):
        tx_fee = 0 if fee is None else fee
        if self.get_balance() < amount + tx_fee:
            print('Not enough funds')
            return
        transaction_hex = self.wallet_handler.create_transaction(amount, address, fee)
        success, transaction_hash = self.wallet_handler.broadcast(transaction_hex)
        if not success:
            print(('Transaction not successfully broadcast, do error handling: {0}'.format(transaction_hash)))
        else:
            print('Transaction successful')
        print(transaction_hex)
        print(success)
        print(transaction_hash)
        return transaction_hash


class ElectrumWalletHandler(object):
    """
    ElectrumWalletHandler ensures the correct opening and closing of the electrum wallet daemon
    """

    def __init__(self, wallet_command=None, wallet_path=None):
        """
        Allows wallet_command to be changed to for example electrum --testnet
        :param wallet_command: command to call wallet
        """
        if wallet_command is None:
            if os.path.exists('/usr/local/bin/electrum'):
                wallet_command = ['/usr/local/bin/electrum']
            else:
                wallet_command = ['/usr/bin/env', 'electrum']
        self.command = wallet_command
        p, e = subprocess.Popen(self.command + ['daemon', 'status'], stdout=subprocess.PIPE).communicate()
        self.not_running_before = b'not running' in p
        if self.not_running_before:
            subprocess.call(self.command + ['daemon', 'start'])
        if wallet_path is None:
            subprocess.call(self.command + ['daemon', 'load_wallet'])
        else:
            print('Using wallet: ', wallet_path)
            subprocess.call(self.command + ['daemon', 'load_wallet', '-w', wallet_path])

    def __del__(self):
        if self.not_running_before:
            subprocess.call(self.command + ['daemon', 'stop'])

    def create_transaction(self, amount, address, fee):
        """
        Create a transaction
        :param amount: amount of bitcoins to be transferred
        :param address: address to transfer to
        :param fee: None for autofee, or specify own fee
        :return: transaction details
        """
        if fee is None:
            transaction = subprocess.check_output(self.command + ['payto', str(address), str(amount)]).decode()
        else:
            transaction = subprocess.check_output(self.command + ['payto', str(address), str(amount), '-f', str(fee)]).decode()
        jtrs = json.loads(transaction)
        return jtrs['hex']

    def broadcast(self, transaction):
        """
        Broadcast a transaction
        :param transaction: hex of transaction
        :return: if successful returns success and
        """
        broadcast = subprocess.check_output(self.command + ['broadcast', transaction]).decode()
        jbr = json.loads(broadcast)
        return tuple(jbr)

    def get_balance(self):
        """
        Return the balance of the default electrum wallet
        :return: balance of default wallet
        """
        output = subprocess.check_output(self.command + ['getbalance']).decode()
        balance_dict = json.loads(output)
        return balance_dict

    def get_addresses(self):
        """
        Return the list of addresses of default wallet
        :return: 
        """
        address = subprocess.check_output(self.command + ['listaddresses']).decode()
        addr = json.loads(address)
        return addr
