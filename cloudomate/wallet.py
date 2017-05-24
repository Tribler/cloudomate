import subprocess
import json
import mechanize

from bs4 import BeautifulSoup
from forex_python.bitcoin import BtcConverter



class Wallet:
    def __init__(self):
        pass

    @staticmethod
    def getrate(currency):
        c = BtcConverter()
        print 1/(c.get_latest_price(currency))

    @staticmethod
    def getcurrentbtcprice(amount, rate):
        price = amount*rate
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
        print addresses

    @staticmethod
    def getfee():
        browser = mechanize.Browser()
        browser.set_handle_robots(False)
        browser.addheaders = [('User-agent', 'Firefox')]
        page = browser.open('https://bitcoinfees.21.co/api/v1/fees/recommended')
        soup = BeautifulSoup(page, 'lxml')
        rates = json.loads(soup.find('p').text)
        satoshiRate = rates['halfHourFee']
        satoshiRate = float(satoshiRate)
        rate = satoshiRate / 100000000
        return rate * 226

    @staticmethod
    def getbitpayfee():
        return 0.000423

    def getfullfee(self):
        return self.getfee() + self.getbitpayfee()

    def payautofee(self, address, amount):
        subprocess.call(['electrum', 'daemon', 'start'])
        subprocess.call(['electrum', 'daemon', 'load_wallet'])
        amount = amount + self.getfee() + self.getbitpayfee()
        if self.getbalance() < amount:
            print 'NotEnoughFunds'
        else:
            output = subprocess.check_output(['electrum', 'payto', str(address), str(amount)])
            temp = json.loads(output)
            hextransaction = temp['hex']
            subprocess.call(['electrum', 'broadcast', hextransaction])
            print 'payment succeeded'
        subprocess.call(['electrum', 'daemon', 'stop'])

    def pay(self, address, amount, fee):
        if self.getbalance() < amount:
            print 'NotEnoughFunds'
        else:
            subprocess.check_output(['electrum', 'payto', address, amount, '-f', fee])
            print 'payment succeeded'

    def emptywallet(self, address):
        if self.getbalance() is not 0.0:
            output = subprocess.check_output(['electrum', 'payto', address, '!'])
            temp = json.loads(output)
            hextransaction = temp['hex']
            subprocess.call(['electrum', 'broadcast', hextransaction])
            print 'Wallet was succesfully emptied'
        else:
            print 'Wallet already empty'
