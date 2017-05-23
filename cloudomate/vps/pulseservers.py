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
        self.configurations = [self._parse_box(box) for box in pricingboxes]
        return self.configurations

    def _parse_box(self, box):
        details = box.findAll('li')
        return VpsOption(
            name = details[0].h4.text,
            price = details[1].h1.text + details[1].span.text,
            cpu = self._beautify_cpu(details[2].strong.text, details[2].find(text=True, recursive=False)),
            ram = details[3].strong.text,
            storage = details[4].strong.text,
            connection = details[5].strong.text,
            bandwidth = details[6].strong.text,
            purchase_url = details[9].a['href']
        )

    def _beautify_cpu(self, cores, speed):
        spl = cores.split()
        return '{0}c/{1}t {2}'.format(spl[0], spl[3], speed[:-4])

    def purchase(self, user_settings, vps_option):
        br = self._create_browser()
        br.open(vps_option.purchase_url)
        br.select_form(predicate = lambda f: 'id' in f.attrs and f.attrs['id'] == 'orderfrm')
        #<div id="configproducterror" class="errorbox"></div>
        br.form['billingcycle'] = ['monthly']
        br.form['hostname'] = user_settings.get('hostname')
        br.form['rootpw'] = user_settings.get('rootpw')
        # OS
        br.form['configoption[3]'] = ['2']
        # Location
        br.form['configoption[9]'] = ['63']
        br.form.new_control('text', 'ajax', {'name': 'ajax', 'value': 1})
        br.form.new_control('text', 'a', {'name': 'a', 'value': 'confproduct'})
        br.form.method = "POST"
        br.submit()

        site = br.response().read()
        print site

if __name__ == '__main__':
    Pulseservers.purchase({},Pulseservers().options()[1])