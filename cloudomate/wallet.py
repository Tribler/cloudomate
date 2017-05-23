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
        subprocess.call(['electrum', 'daemon', 'start'])
        subprocess.call(['electrum', 'daemon', 'load_wallet'])
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