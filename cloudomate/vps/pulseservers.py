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
        vps_options = [self._parse_box(box) for box in pricingboxes]
        return vps_options

    def _parse_box(self, box):
        details = box.findAll('li')
        return VpsOption(
            name = details[0].h4.text,
            price = details[1].h4.text + details[1].span.text,
            cpu = self._beautify_cpu(details[2].h4.text, details[2].find(text=True, recursive=False))
        )

    def _beautify_cpu(self, cores, speed):
        spl = cores.split()
        return '{0}c/{1}t {2}'.format(spl[0], spl[3], speed[:-4])

    def purchase(self, user_settings, vps_option):
        print("Purchase")
        pass
