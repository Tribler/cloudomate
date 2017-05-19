import itertools

import mechanize
from bs4 import BeautifulSoup

from cloudomate.vps.hoster import Hoster
from cloudomate.vps.vpsoption import VpsOption


class RockHoster(Hoster):
    name = "rockhoster"
    website = "https://rockhoster.com/"
    required_settings = ["rootpw"]

    def options(self):
        return self.crawl_options()

    def purchase(self, user_settings, vps_option):
        print("Purchase")
        pass

    def __init__(self):
        pass

    def crawl_options(self):
        browser = mechanize.Browser()
        browser.set_handle_robots(False)
        browser.addheaders = [('User-agent', 'FireFox')]

        openvz_hosting_page = browser.open("https://rockhoster.com/linux.html")
        options = self.parse_openvz_hosting(openvz_hosting_page.get_data())

        kvm_hosting_page = browser.open("https://rockhoster.com/windows-vps")
        options = itertools.chain(options, self.parse_kvm_hosting(kvm_hosting_page.get_data()))
        self.configurations = list(options)
        return self.configurations

    def parse_openvz_hosting(self, page):
        soup = BeautifulSoup(page, "lxml")
        details = soup.findAll('div', {'class': 'pacdetails'})
        for column in details:
            yield self.parse_openvz_option(column)

    def parse_openvz_option(self, column):
        elements = column.findAll("li")
        option = VpsOption()
        option.disk = elements[0].text
        option.ram = elements[1].text
        option.bandwidth = 'unmetered'
        option.cpu = elements[3].text
        option.connection = elements[5].text
        option.name = column.div.h2.string
        option.price = column.div.strong.text
        return option

    def parse_kvm_hosting(self, page):
        soup = BeautifulSoup(page, "lxml")
        details = soup.findAll('div', {'class': 'pacdetails'})
        for column in details:
            yield self.parse_kvm_option(column)

    def parse_kvm_option(self, column):
        elements = column.findAll("li")
        option = VpsOption()
        option.storage = elements[0].text
        option.ram = elements[1].text
        option.bandwidth = 'unmetered'
        option.cpu = elements[3].text
        option.connection = '1000 Mbps'
        option.name = column.div.h2.string
        option.price = column.div.strong.text
        return option


if __name__ == "__main__":
    RockHoster().crawl_options()
