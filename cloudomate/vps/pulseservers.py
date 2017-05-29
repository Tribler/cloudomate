import sys
from bs4 import BeautifulSoup as soup

from cloudomate.gateway.coinbase import extract_info
from cloudomate.vps.hoster import Hoster
from cloudomate.vps.vpsoption import VpsOption


class Pulseservers(Hoster):
    '''
    PulseServers contains the logic to view hosting configurations and to 
    purchase servers at Pulseservers.
    '''
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
        'password',
        'hostname',
        'rootpw'
    ]

    def __init__(self):
        super(Pulseservers, self).__init__()

    def start(self):
        '''
        Open browser to hoster website and return parsed options
        :return: parsed options
        '''
        response = self.br.open('https://pulseservers.com/vps-linux.html')
        return self.parse_options(response)

    def parse_options(self, response):
        '''
        Parse options of hosting configurations
        :param response: Site to be parsed
        :return: list of configurations
        '''
        site = soup(response.read(), 'lxml')
        pricingboxes = site.findAll('div', {'class': 'pricing-box'})
        self.configurations = [self._parse_box(box) for box in pricingboxes]
        return self.configurations

    def _parse_box(self, box):
        '''
        Parse a single hosting configuration
        :param box: Div containing hosting details
        :return: VpsOption containing hosting details
        '''
        details = box.findAll('li')
        return VpsOption(
            name=details[0].h4.text,
            price=details[1].h1.text + details[1].span.text,
            cpu=self._beautify_cpu(details[2].strong.text, details[2].find(text=True, recursive=False)),
            ram=details[3].strong.text,
            storage=details[4].strong.text,
            connection=details[5].strong.text,
            bandwidth=details[6].strong.text,
            purchase_url=details[9].a['href']
        )

    def _beautify_cpu(self, cores, speed):
        '''
        Format cores and speed to fit cpu column
        :param cores: cores text
        :param speed: speed text
        :return: formatted string
        '''
        spl = cores.split()
        return '{0}c/{1}t {2}'.format(spl[0], spl[3], speed[:-4])

    def register(self, user_settings, vps_option):
        '''
        Register at Pulseservers provider and pay through coinbase
        :param user_settings: 
        :param vps_option: 
        :return: 
        '''
        self.br.open(vps_option.purchase_url)
        self.br.select_form(predicate=lambda f: 'id' in f.attrs and f.attrs['id'] == 'orderfrm')
        self.fill_in_server_form(user_settings)
        self.br.submit()
        next = self.br.open('https://www.pulseservers.com/billing/cart.php?a=confdomains')
        # redirects to https://www.pulseservers.com/billing/cart.php?a=view

        self.br.select_form(predicate=lambda f: 'id' in f.attrs and f.attrs['id'] == 'mainfrm')
        self.fill_in_user_form(user_settings)

        promobutton = self.br.form.find_control(name="validatepromo")
        promobutton.disabled = True

        print(self.br.form)

        page = self.br.submit()

        if 'checkout' in page.geturl():
            contents = soup(page.read(), 'lxml')
            errors = contents.find('div', {'class': 'errorbox'})
            print(errors)
            print(page.read())
            sys.exit(1)

        print(page.read())

        self.br.select_form(nr=0)
        page = self.br.submit()

        amount, address = extract_info(page.geturl())
        return amount, address

    def fill_in_server_form(self, user_settings):
        '''
        Fill in the form with user information
        :param user_settings: settings
        :return: 
        '''
        # <div id="configproducterror" class="errorbox"></div>
        self.br.form['billingcycle'] = ['monthly']
        self.br.form['hostname'] = user_settings.get('hostname')
        self.br.form['rootpw'] = user_settings.get('rootpw')
        # OS
        # self.br.form['configoption[3]'] = ['2']
        # Location
        # self.br.form['configoption[9]'] = ['63']
        self.br.form.new_control('text', 'ajax', {'name': 'ajax', 'value': 1})
        self.br.form.new_control('text', 'a', {'name': 'a', 'value': 'confproduct'})
        self.br.form.method = "POST"

    def fill_in_user_form(self, user_settings):
        '''
        Fill in form with registration information
        :param user_settings: user info
        :return: 
        '''
        self.br.form['firstname'] = user_settings.get("firstname")
        self.br.form['lastname'] = user_settings.get("lastname")
        self.br.form['email'] = user_settings.get("email")
        self.br.form['phonenumber'] = user_settings.get("phonenumber")
        self.br.form['companyname'] = user_settings.get("companyname")
        self.br.form['address1'] = user_settings.get("address")
        self.br.form['city'] = user_settings.get("city")
        countrycode = user_settings.get("countrycode")
        self.br.form['country'] = [countrycode]
        self.br.form['state'] = user_settings.get("state")
        self.br.form['postcode'] = user_settings.get("zipcode")
        self.br.form['password'] = user_settings.get("password")
        self.br.form['password2'] = user_settings.get("password")
        self.br.form['paymentmethod'] = ['coinbase']
        self.br.find_control('accepttos').items[0].selected = True


if __name__ == '__main__':
    Pulseservers.purchase({}, Pulseservers().options()[1])
