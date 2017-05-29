from bs4 import BeautifulSoup

from cloudomate.gateway.bitpay import extract_info
from cloudomate.vps.hoster import Hoster
from cloudomate.vps.vpsoption import VpsOption


class BlueAngelHost(Hoster):
    name = "blueangelhost"
    website = "https://www.blueangelhost.com/"
    required_settings = [
        'firstname',
        'lastname',
        'email',
        'address',
        'city',
        'state',
        'zipcode',
        'phonenumber'
        'password',
        'hostname',
        'rootpw',
        'ns1',
        'ns2'
    ]

    def __init__(self):
        super(BlueAngelHost, self).__init__()

    def register(self, user_settings, vps_option):
        """
        Register RockHoster provider, pay through CoinBase
        :param user_settings: 
        :param vps_option: 
        :return: 
        """
        self.br.open(vps_option.purchase_url)
        self.br.select_form(nr=2)
        self.fill_in_server_form(user_settings)
        self.br.submit()
        self.br.open('https://www.billing.blueangelhost.com/cart.php?a=view')
        self.br.follow_link(text_regex='Checkout')
        self.br.select_form(nr=2)
        self.fill_in_user_form(user_settings)
        self.br.submit()
        self.br.select_form(nr=0)
        page = self.br.submit()
        url = page.geturl()
        amount, address = extract_info(url)
        return amount, address

    def fill_in_server_form(self, user_settings):
        """
        Fills in the form containing server configuration
        :param user_settings: settings
        :return: 
        """
        self.br.form['hostname'] = user_settings.get('hostname')
        self.br.form['rootpw'] = user_settings.get('rootpw')
        self.br.form['ns1prefix'] = user_settings.get('ns1')
        self.br.form['ns2prefix'] = user_settings.get('ns2')
        self.br.form['configoption[72]'] = ['87']  # Ubuntu
        self.br.form['configoption[73]'] = ['91']  # 64 bit
        self.br.form.new_control('text', 'ajax', {'name': 'ajax', 'value': 1})
        self.br.form.new_control('text', 'a', {'name': 'a', 'value': 'confproduct'})
        self.br.form.method = "POST"

    def fill_in_user_form(self, user_settings):
        """
        Fills in the form with user information
        :param user_settings: settings
        :return: 
        """
        self.br.form['firstname'] = user_settings.get('firstname')
        self.br.form['lastname'] = user_settings.get('lastname')
        self.br.form['email'] = user_settings.get('email')
        self.br.form['phonenumber'] = user_settings.get('phonenumber')
        self.br.form['companyname'] = user_settings.get('companyname')
        self.br.form['address1'] = user_settings.get('address')
        self.br.form['city'] = user_settings.get('city')
        self.br.form['country'] = [user_settings.get('countrycode')]
        self.br.form['state'] = user_settings.get('state')
        self.br.form['postcode'] = user_settings.get('zipcode')
        self.br.form['customfield[4]'] = ['Google']
        self.br.form['password'] = user_settings.get('password')
        self.br.form['password2'] = user_settings.get('password')
        self.br.form['paymentmethod'] = ['bitpay']
        self.br.find_control('accepttos').items[0].selected = True

    def start(self):
        blue_page = self.br.open('https://www.blueangelhost.com/openvz-vps/')
        return self.parse_options(blue_page)

    def parse_options(self, page):
        soup = BeautifulSoup(page, 'lxml')
        month = soup.find('div', {'id': 'monthly_price'})
        details = month.findAll('div', {'class': 'plan_table'})
        for column in details:
            yield self.parse_blue_options(column)

    @staticmethod
    def parse_blue_options(column):
        option = VpsOption()
        option.name = column.find('div', {'class': 'plan_title'}).find('h4').text
        option.price = column.find('div', {'class': 'plan_price_m'}).text.strip()
        option.price = option.price.split('$')[1]
        option.price = option.price.split('/')[0]
        planinfo = column.find('ul', {'class': 'plan_info_list'})
        info = planinfo.findAll('li')
        option.cpu = info[0].text.split(":")[1].strip()
        option.ram = info[1].text.split(":")[1].strip()
        option.storage = info[2].text.split(":")[1].strip()
        option.connection = info[3].text.split(":")[1].strip()
        option.bandwidth = info[4].text.split("h")[1].strip()
        option.purchase_url = column.find('a')['href']
        return option


if __name__ == "__main__":
    BlueAngelHost.start()
