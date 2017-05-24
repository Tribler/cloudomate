import mechanize
from bs4 import BeautifulSoup

from cloudomate.vps.clientarea import ClientArea
from cloudomate.vps.hoster import Hoster
from cloudomate.vps.vpsoption import VpsOption
from cloudomate.gateway.bitpay import extract_info
from cloudomate import wallet


class BlueAngelHost(Hoster):
    name = "blueangelhost"
    website = "https://www.blueangelhost.com/"
    required_settings = ["rootpw"]
    clientarea_url = 'https://www.billing.blueangelhost.com/clientarea.php'

    def purchase(self, user_settings, vps_option):
        """
        Purchase a RockHoster VPS.
        :param user_settings: settings
        :param vps_option: server configuration
        :return: 
        """
        print("Purchase")
        self.register(user_settings, vps_option)
        pass

    def register(self, user_settings, vps_option):
        """
        Register RockHoster provider, pay through CoinBase
        :param user_settings: 
        :param vps_option: 
        :return: 
        """
        self.browser.open(vps_option.purchase_url)
        self.browser.select_form(nr=2)
        self.fill_in_server_form(user_settings)
        self.browser.submit()
        self.browser.open('https://www.billing.blueangelhost.com/cart.php?a=view')
        self.browser.follow_link(text_regex='Checkout')
        self.browser.select_form(nr=2)
        self.fill_in_user_form(user_settings)
        self.browser.submit()
        self.browser.select_form(nr=0)
        page = self.browser.submit()
        url = page.geturl()
        (amount, address) = extract_info(url)
        print('Pay', amount, 'to', address)
        # commented out so we don't accidentally buy servers
        # amount = float(amount)
        # fee = wallet.Wallet().getfee()
        # wallet.Wallet().pay(address, amount, fee)

    def fill_in_server_form(self, user_settings):
        """
        Fills in the form containing server configuration
        :param user_settings: settings
        :return: 
        """
        self.browser.form['hostname'] = user_settings.get('hostname')
        self.browser.form['rootpw'] = user_settings.get('rootpw')
        self.browser.form['ns1prefix'] = user_settings.get('ns1')
        self.browser.form['ns2prefix'] = user_settings.get('ns2')
        self.browser.form['configoption[72]'] = ['87']  # Ubuntu
        self.browser.form['configoption[73]'] = ['91']  # 64 bit
        self.browser.form.new_control('text', 'ajax', {'name': 'ajax', 'value': 1})
        self.browser.form.new_control('text', 'a', {'name': 'a', 'value': 'confproduct'})
        self.browser.form.method = "POST"

    def fill_in_user_form(self, user_settings):
        """
        Fills in the form with user information
        :param user_settings: settings
        :return: 
        """
        self.browser.form['firstname'] = user_settings.get('firstname')
        self.browser.form['lastname'] = user_settings.get('lastname')
        self.browser.form['email'] = user_settings.get('email')
        self.browser.form['phonenumber'] = user_settings.get('phonenumber')
        self.browser.form['companyname'] = user_settings.get('companyname')
        self.browser.form['address1'] = user_settings.get('address')
        self.browser.form['city'] = user_settings.get('city')
        self.browser.form['country'] = [user_settings.get('countrycode')]
        self.browser.form['state'] = user_settings.get('state')
        self.browser.form['postcode'] = user_settings.get('zipcode')
        self.browser.form['customfield[4]'] = ['Google']
        self.browser.form['password'] = user_settings.get('password')
        self.browser.form['password2'] = user_settings.get('password')
        self.browser.form['paymentmethod'] = ['bitpay']
        self.browser.find_control('accepttos').items[0].selected = True

    def options(self):
        options = self.start()
        self.configurations = list(options)
        return self.configurations

    def __init__(self):
        self.browser = self._create_browser()
        pass

    def start(self):
        browser = mechanize.Browser()
        browser.set_handle_robots(False)
        browser.addheaders = [('User-agent', 'Firefox')]

        blue_page = browser.open('https://www.blueangelhost.com/openvz-vps/')
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

    def get_status(self, user_settings):
        email = user_settings.get('email')
        password = user_settings.get('password')
        clientarea = ClientArea(self.browser, self.clientarea_url, email, password)
        clientarea.print_services()

    def set_rootpw(self, user_settings):
        email = user_settings.get('email')
        password = user_settings.get('password')
        clientarea = ClientArea(self.browser, self.clientarea_url, email, password)
        rootpw = user_settings.get('rootpw')
        if 'number' in user_settings.config:
            clientarea.set_rootpw(rootpw, int(user_settings.get('number')))
        else:
            clientarea.set_rootpw(rootpw)

    def get_ip(self, user_settings):
        email = user_settings.get('email')
        password = user_settings.get('password')
        clientarea = ClientArea(self.browser, self.clientarea_url, email, password)
        client_data_url = 'https://www.billing.blueangelhost.com/modules/servers/solusvmpro/get_client_data.php'
        if 'number' in user_settings.config:
            clientarea.get_ip(client_data_url, int(user_settings.get('number')))
        else:
            clientarea.get_ip(client_data_url)
