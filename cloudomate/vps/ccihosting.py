import mechanize
from bs4 import BeautifulSoup

from cloudomate.vps.hoster import Hoster
from cloudomate.vps.vpsoption import VpsOption


class CCIHosting(Hoster):
    name = "ccihosting"
    website = "http://www.ccihosting.com/"
    required_settings = ["rootpw"]

    def purchase(self, user_settings, vps_option):
        print 'Purchase'
        pass

    def options(self):
        options = start()
        self.configurations = list(options)
        return self.configurations

    def __init__(self):
        pass


def start(self):
    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    browser.addheaders = [('User-agent', 'Firefox')]

    cci_page = browser.open('http://www.ccihosting.com/vps.php')
    return parse_options(cci_page)


def parse_options(self, page):
    soup = BeautifulSoup(page, 'lxml')
    tables = soup.findAll('div', {'class': 'box5'})
    for column in tables:
        yield parse_cci_options(column)


def parse_cci_options(self, column):
    option = VpsOption()
    option.name = column.find('div', {'class': 'boxtitle'}).text.split('S')[1]
    option.price = column.find('div', {'class': 'PriceTag'}).find('span').text.split('U')[0]
    planinfo = column.find('ul')
    info = planinfo.findAll('li')
    option.cpu = info[1].text.split("CPU")[0] + info[1].text.split("CPU")[1]
    option.ram = info[2].text.split("R")[0]
    option.storage = info[3].text.split("S")[0]
    option.bandwidth = info[4].text.split("Ba")[0]
    option.connection = info[5].text.split("/")[0]
    option.purchase_url = column.find('a')['href']
    return option


if __name__ == "__main__":
    start()
