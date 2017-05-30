import json
import mechanize
import subprocess
from bs4 import BeautifulSoup

from forex_python.bitcoin import BtcConverter

class Wallet:
    AVG_TX_SIZE = 226
    BTC_TO_SATOSHI = 1.0 / 100000000

    @staticmethod
    def getrate():
        b = BtcConverter()
        rate = 1 / b.get_latest_price('USD')
        return rate

    @staticmethod
    def getcurrentbtcprice(amount, rate):
        price = amount * rate
        return price

    @staticmethod
    def getbalance():
        balance = str(subprocess.check_output(['electrum', 'getbalance']))
        blance = json.loads(balance)
        confirmed = blance['confirmed']
        unconfirmed = blance.get('unconfirmed', 0.0)
        return float(confirmed) + float(unconfirmed)

    @staticmethod
    def getaddresses():
        address = str(subprocess.check_output(['electrum', 'listaddresses']))
        addr = json.loads(address)
        addresses = addr[0]
        return addresses

    @staticmethod
    def getfee():
        browser = mechanize.Browser()
        browser.set_handle_robots(False)
        browser.addheaders = [('User-agent', 'Firefox')]
        page = browser.open('https://bitcoinfees.21.co/api/v1/fees/recommended')
        soup = BeautifulSoup(page, 'lxml')
        rates = json.loads(soup.find('p').text)
        satoshirate = rates['halfHourFee']
        satoshirate = float(satoshirate)
        fee = satoshirate * Wallet.BTC_TO_SATOSHI
        return fee * Wallet.AVG_TX_SIZE

    @staticmethod
    def getbitpayfee():
        return 0.000423

    def getfullfee(self):
        fullfee = self.getfee() + self.getbitpayfee()
        return fullfee

    def payautofee(self, address, amount):
        with ElectrumWalletHandler():
            amount = amount + self.getfee() + self.getbitpayfee()
            if self.getbalance() < amount:
                print 'NotEnoughFunds'
            else:
                output = subprocess.check_output(['electrum', 'payto', str(address), str(amount)])
                temp = json.loads(output)
                hextransaction = temp['hex']
                subprocess.call(['electrum', 'broadcast', hextransaction])
                print 'payment succeeded'

    def pay(self, address, amount, fee):
        with ElectrumWalletHandler():
            if self.getbalance() < amount + fee:
                print 'NotEnoughFunds'
            else:
                subprocess.check_output(['electrum', 'payto', str(address), str(amount), '-f', str(fee)])
                print 'payment succeeded'

    def emptywallet(self, address):
        with ElectrumWalletHandler():
            if self.getbalance() is not 0.0:
                output = subprocess.check_output(['electrum', 'payto', address, '!'])
                temp = json.loads(output)
                hextransaction = temp['hex']
                subprocess.call(['electrum', 'broadcast', hextransaction])
                print 'Wallet was successfully emptied'
            else:
                print 'Wallet already empty'


class ElectrumWalletHandler(object):
    def __enter__(self):
        subprocess.call(['electrum', 'daemon', 'start'])
        subprocess.call(['electrum', 'daemon', 'load_wallet'])

    def __exit__(self):
        subprocess.call(['electrum', 'daemon', 'stop'])
