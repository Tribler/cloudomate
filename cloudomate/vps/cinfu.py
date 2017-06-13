from bs4 import BeautifulSoup

from cloudomate.gateway import coinbase
from cloudomate.vps.clientarea import ClientArea
from cloudomate.vps.solusvm_hoster import SolusvmHoster
from cloudomate.vps.vpsoption import VpsOption
from cloudomate.wallet import determine_currency


class Cinfu(SolusvmHoster):
    name = "cinfu"
    website = "https://www.cinfu.com/"
    clientarea_url = ""
    required_settings = [
        'firstname',
        'lastname',
        'email',
        'phonenumber',
        'address',
        'city',
        'countrycode',
        'state',
        'zipcode',
        'password',
        'hostname',
        'rootpw'
    ]
    gateway = coinbase

    def __init__(self):
        super(Cinfu, self).__init__()

    def start(self):
        cinfu_page = self.br.open('https://www.cinfu.com/vps/')
        return self.parse_options(cinfu_page)

    def parse_options(self, page):
        soup = BeautifulSoup(page, 'lxml')
        table = soup.find('table', {'class': 'table1'})
        return list(self.parse_german_options(table))

    def parse_german_options(self, table):
        info = table.findAll('tr')
        head = True
        j = 1
        names = [""] * 8
        ram = [""] * 8
        storage = [""] * 8
        cpu = [""] * 8
        price = [""] * 8
        link = [""] * 8
        for item in info:
            if head:
                self.fill_array(names, 'th', item, False)
                head = False
            else:
                if j == 1:
                    self.fill_array(ram, 'td', item, False)
                if j == 2:
                    self.fill_array(storage, 'td', item, False)
                if j == 4:
                    self.fill_array(cpu, 'td', item, False)
                if j == 8:
                    self.fill_array(price, 'td', item, False)
                if j == 12:
                    self.fill_array(link, 'td', item, True)
                j = j + 1
        for k in range(8):
            yield self.fill_german_options(names[k],ram[k],storage[k],cpu[k],price[k],link[k])


    def fill_german_options(self, names, rams, storages, cpus, prices,links):
        return VpsOption(
            name=names,
            price=float(prices.split('$')[1]),
            currency=determine_currency(prices),
            cpu=int(cpus.split("x")[0]),
            ram=float(rams.split("M")[0]) / 1024,
            storage=float(storages.split("G")[0]),
            bandwidth='unmetered',
            connection=100,
            purchase_url= links
        )

    def fill_array(self, array, type, item, link):
        if link:
            temp = item.findAll(type)
            i = 0
            for name in temp[1:]:
                array[i] = name.find('a')['href']
                i = i + 1
        else:
            temp = item.findAll(type)
            i = 0
            for name in temp[1:]:
                array[i] = name.text
                i = i + 1


Cinfu().start()
