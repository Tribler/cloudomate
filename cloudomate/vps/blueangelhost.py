import mechanize
from bs4 import BeautifulSoup

from cloudomate.vps.hoster import Hoster
from cloudomate.vps.vpsoption import VpsOption


class BlueAngelHost(Hoster):
    name = "blueangelhost"
    website = "https://www.blueangelhost.com/"
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

    blue_page = browser.open('https://www.blueangelhost.com/openvz-vps/')
    return parse_options(blue_page)


def parse_options(self, page):
    soup = BeautifulSoup(page, 'lxml')
    month = soup.find('div', {'id': 'monthly_price'})
    details = month.findAll('div', {'class': 'plan_table'})
    for column in details:
        yield parse_blue_options(column)


def parse_blue_options(self, column):
    option = VpsOption()
    option.name = column.find('div', {'class': 'plan_title'}).find('h4').text
    option.price = column.find('div', {'class': 'plan_price_m'}).text
    planinfo = column.find('ul', {'class': 'plan_info_list'})
    info = planinfo.findAll('li')
    option.cpu = info[0].text.split(":")[1]
    option.ram = info[1].text.split(":")[1]
    option.storage = info[2].text.split(":")[1]
    option.connection = info[3].text.split(":")[1]
    option.bandwidth = info[4].text.split("h")[1]
    option.purchase_url = column.find('a')['href']
    return option


if __name__ == "__main__":
    start()
