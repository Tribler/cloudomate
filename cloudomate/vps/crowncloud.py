import mechanize
from bs4 import BeautifulSoup

from cloudomate.vps.hoster import Hoster
from cloudomate.vps.vpsoption import VpsOption


class CrownCloud(Hoster):
    name = "crowncloud"
    website = "http://crowncloud.net/"
    required_settings = ["rootpw"]
    browser = None

    def __init__(self):
        pass

    def purchase(self, user_settings, vps_option):
        print 'Purchase'
        pass

    def options(self):
        options = self.start()
        self.configurations = list(options)
        return self.configurations


    def start(self):
        browser = mechanize.Browser()
        browser.set_handle_robots(False)
        browser.addheaders = [('User-agent', 'Firefox')]

        clown_page = browser.open('http://crowncloud.net/openvz.php')
        return self.parse_options(clown_page)


    def parse_options(self, page):
        soup = BeautifulSoup(page, 'lxml')
        tables = soup.findAll('table')
        for details in tables:
            for column in details.findAll('tr'):
                if len(column.findAll('td')) > 0:
                    yield self.parse_clown_options(column)


    @staticmethod
    def parse_clown_options(column):
        elements = column.findAll('td')
        option = VpsOption()
        option.name = elements[0].text
        option.ram = elements[1].text
        option.storage = elements[2].text
        option.cpu = elements[3].text
        option.bandwidth = elements[4].text
        option.connection = elements[7].text
        option.price = elements[8].text
        option.purchase_url = elements[9].find('a')['href']
        return option


if __name__ == "__main__":
    CrownCloud.start()
