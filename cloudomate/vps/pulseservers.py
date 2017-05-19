from mechanize import Browser
from bs4 import BeautifulSoup as soup

from cloudomate.vps.hoster import Hoster
from cloudomate.vps.vpsoption import VpsOption


class Pulseservers(Hoster):
    name = "pulseservers"
    website = "https://pulseservers.com/"
    required_settings = []

    def options(self):
        br = self._create_browser()
        response = br.open('https://pulseservers.com/vps-linux.html')
        site = soup(response.read(), 'lxml')
        pricingboxes = site.findAll('div', {'class': 'pricing-box'})
        for box in


    def purchase(self, user_settings, vps_option):
        print("Purchase")
        pass
