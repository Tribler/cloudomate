import subprocess
import json


class Wallet:
    def __init__(self):
        pass

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

    def payautofee(self, address, amount):
        if self.getbalance() < amount:
            print 'NotEnoughFunds'
        else:
            output = subprocess.check_output(['electrum', 'payto', address, str(amount)])
            temp = json.loads(output)
            hextransaction = temp['hex']
            subprocess.call(['electrum', 'broadcast', hextransaction])
            print 'payment succeeded'

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
