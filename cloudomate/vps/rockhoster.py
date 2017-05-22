import itertools

from bs4 import BeautifulSoup

from cloudomate.vps.hoster import Hoster
from cloudomate.vps.vpsoption import VpsOption


class RockHoster(Hoster):
    name = "rockhoster"
    website = "https://rockhoster.com/"
    required_settings = ["rootpw"]

    def __init__(self):
        pass

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
        br = self._create_browser()

        br.open(vps_option.purchase_url)
        br.select_form(nr=4)
        self.fill_in_server_form(br, user_settings)
        br.submit()
        br.open('https://rockhoster.com/cloud/cart.php?a=view')
        br.follow_link(text_regex=r"Checkout")
        br.select_form(nr=4)
        self.fill_in_user_form(br, user_settings)
        br.submit()
        br.follow_link(url_regex="coinbase")

    @staticmethod
    def fill_in_server_form(br, user_settings):
        """
        Fills in the form containing server configuration.
        :param br: browser
        :param user_settings: settings
        :return: 
        """
        br.form['hostname'] = user_settings.get("hostname")
        br.form['rootpw'] = user_settings.get("rootpw")
        br.form['ns1prefix'] = user_settings.get("ns1")
        br.form['ns2prefix'] = user_settings.get("ns2")
        br.form['configoption[20]'] = ['53']  # Paris
        br.form['configoption[2]'] = ['13']
        br.form.new_control('text', 'ajax', {'name': 'ajax', 'value': 1})
        br.form.new_control('text', 'a', {'name': 'a', 'value': 'confproduct'})
        br.form.method = "POST"

    @staticmethod
    def fill_in_user_form(br, user_settings):
        """
        Fills in the form with user information.
        :param br: browser
        :param user_settings: settings
        :return: 
        """
        br.form['firstname'] = user_settings.get("firstname")
        br.form['lastname'] = user_settings.get("lastname")
        br.form['email'] = user_settings.get("email")
        br.form['phonenumber'] = user_settings.get("phonenumber")
        br.form['companyname'] = user_settings.get("companyname")
        br.form['address1'] = user_settings.get("address")
        br.form['city'] = user_settings.get("city")
        countrycode = user_settings.get("countrycode")

        # State input changes based on country: USA (default) -> Select, Other -> Text
        br.form['state'] = user_settings.get("state")
        br.form['postcode'] = user_settings.get("zipcode")
        br.form['country'] = [countrycode]
        br.form['password'] = user_settings.get("password")
        br.form['password2'] = user_settings.get("password")
        br.form['paymentmethod'] = ['coinbase']
        br.find_control('accepttos').items[0].selected = True

    def options(self):
        return self.crawl_options()

    def crawl_options(self):
        """
        Linux (OpenVZ) and Windows (KVM) pages are slightly different, therefore their pages are parsed by different 
        methoods. Windows configurations allow a selection of Linux distributions, but not vice-versa.
        :return: possible configurations.
        """
        browser = self._create_browser()

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

    @staticmethod
    def parse_openvz_option(column):
        elements = column.findAll("li")
        option = VpsOption()
        option.storage = elements[0].text.split(": ")[1]
        option.ram = elements[1].text.split("RAM: ")[1]
        option.bandwidth = 'unmetered'
        option.cpu = elements[3].text
        option.connection = elements[5].text.split(": ")[1]
        option.name = column.div.h2.string
        option.price = column.div.strong.text
        option.purchase_url = column.find('div', {'class': 'bottom'}).a['href']
        return option

    def parse_kvm_hosting(self, page):
        soup = BeautifulSoup(page, "lxml")
        details = soup.findAll('div', {'class': 'pacdetails'})
        for column in details:
            yield self.parse_kvm_option(column)

    @staticmethod
    def parse_kvm_option(column):
        elements = column.findAll("li")
        option = VpsOption()
        option.storage = elements[0].text.split(": ")[1]
        option.ram = elements[1].text.split("RAM:")[1].strip()
        option.bandwidth = 'unmetered'
        option.cpu = elements[3].text
        option.connection = '1000 Mbps'
        option.name = column.div.h2.string
        option.price = column.div.strong.text
        option.purchase_url = column.find('div', {'class': 'bottom'}).a['href']
        return option


if __name__ == "__main__":
    RockHoster().crawl_options()
