from bs4 import BeautifulSoup as soup

from cloudomate.vps.hoster import Hoster
from cloudomate.vps.vpsoption import VpsOption

from cloudomate.gateway.coinbase import extract_info

import sys


class Pulseservers(Hoster):
    """
    PulseServers contains the logic to view hosting configurations and to 
    purchase servers at Pulseservers.
    """
    name = "pulseservers"
    website = "https://pulseservers.com/"
    required_settings = [
        'firstname',
        'lastname',
        'email',
        'phonenumber',
        'address',
        'city',
        'state',
        'zipcode',
        'phonenumber',
        'password',
        'hostname',
        'rootpw'
    ]

    def options(self):
        """
        Retrieve hosting options at Pulseservers.
        :return: A list of hosting options
        """
        options = self.start()
        self.configurations = list(options)
        return self.configurations

    def start(self):
        """
        Open browser to hoster website and return parsed options
        :return: parsed options
        """
        self.browser = self._create_browser()
        response = self.browser.open('https://pulseservers.com/vps-linux.html')
        return self.parse_options(response)

    def parse_options(self, response):
        """
        Parse options of hosting configurations
        :param response: Site to be parsed
        :return: list of configurations
        """
        site = soup(response.read(), 'lxml')
        pricingboxes = site.findAll('div', {'class': 'pricing-box'})
        self.configurations = [self._parse_box(box) for box in pricingboxes]
        return self.configurations

    def _parse_box(self, box):
        """
        Parse a single hosting configuration
        :param box: Div containing hosting details
        :return: VpsOption containing hosting details
        """
        details = box.findAll('li')
        storage = details[4].strong.text
        if storage == '1TB':
            storage = '1024'
        else:
            storage = storage.split('G')[0]

        connection = details[5].strong.text.split('G')[0]
        connection = int(connection) * 1000
        return VpsOption(
            name=details[0].h4.text,
            price=details[1].h1.text.split('$')[1] + details[1].span.text.split('/')[0],
            cpu=details[2].strong.text.split('C')[0],
            ram=details[3].strong.text.split('G')[0],
            storage=storage,
            connection=str(connection),
            bandwidth=details[6].strong.text,
            purchase_url=details[9].a['href']
        )

    def _beautify_cpu(self, cores, speed):
        """
        Format cores and speed to fit cpu column
        :param cores: cores text
        :param speed: speed text
        :return: formatted string
        """
        spl = cores.split()
        return '{0}c/{1}t {2}'.format(spl[0], spl[3], speed[:-4])

    def purchase(self, user_settings, vps_option):
        """
        Purchase a Pulseserver VPS
        :param user_settings: settings
        :param vps_option: server configuration
        :return: 
        """
        print('Purchase')
        self.register(user_settings, vps_option)
        pass

    def register(self, user_settings, vps_option):
        """
        Register at Pulseservers provider and pay through coinbase
        :param user_settings: 
        :param vps_option: 
        :return: 
        """
        self.browser.open(vps_option.purchase_url)
        self.browser.select_form(predicate=lambda f: 'id' in f.attrs and f.attrs['id'] == 'orderfrm')
        self.fill_in_server_form(user_settings)
        self.browser.submit()
        next = self.browser.open('https://www.pulseservers.com/billing/cart.php?a=confdomains')
        # redirects to https://www.pulseservers.com/billing/cart.php?a=view

        self.browser.select_form(predicate=lambda f: 'id' in f.attrs and f.attrs['id'] == 'mainfrm')
        self.fill_in_user_form(user_settings)

        promobutton = self.browser.form.find_control(name="validatepromo")
        promobutton.disabled = True

        print(self.browser.form)

        page = self.browser.submit()

        if 'checkout' in page.geturl():
            contents = soup(page.read(), 'lxml')
            errors = contents.find('div', {'class': 'errorbox'})
            print(errors)
            print(page.read())
            sys.exit(1)

        print(page.read())

        self.browser.select_form(nr=0)
        page = self.browser.submit()

        (amount, address) = extract_info(page.geturl())

    def fill_in_server_form(self, user_settings):
        """
        Fill in the form with user information
        :param user_settings: settings
        :return: 
        """
        # <div id="configproducterror" class="errorbox"></div>
        self.browser.form['billingcycle'] = ['monthly']
        self.browser.form['hostname'] = user_settings.get('hostname')
        self.browser.form['rootpw'] = user_settings.get('rootpw')
        # OS
        # self.browser.form['configoption[3]'] = ['2']
        # Location
        # self.browser.form['configoption[9]'] = ['63']
        self.browser.form.new_control('text', 'ajax', {'name': 'ajax', 'value': 1})
        self.browser.form.new_control('text', 'a', {'name': 'a', 'value': 'confproduct'})
        self.browser.form.method = "POST"

    def fill_in_user_form(self, user_settings):
        """
        Fill in form with registration information
        :param user_settings: user info
        :return: 
        """
        self.browser.form['firstname'] = user_settings.get("firstname")
        self.browser.form['lastname'] = user_settings.get("lastname")
        self.browser.form['email'] = user_settings.get("email")
        self.browser.form['phonenumber'] = user_settings.get("phonenumber")
        self.browser.form['companyname'] = user_settings.get("companyname")
        self.browser.form['address1'] = user_settings.get("address")
        self.browser.form['city'] = user_settings.get("city")
        countrycode = user_settings.get("countrycode")
        self.browser.form['country'] = [countrycode]
        self.browser.form['state'] = user_settings.get("state")
        self.browser.form['postcode'] = user_settings.get("zipcode")
        self.browser.form['password'] = user_settings.get("password")
        self.browser.form['password2'] = user_settings.get("password")
        self.browser.form['paymentmethod'] = ['coinbase']
        self.browser.find_control('accepttos').items[0].selected = True


if __name__ == '__main__':
    Pulseservers.purchase({}, Pulseservers().options()[1])
