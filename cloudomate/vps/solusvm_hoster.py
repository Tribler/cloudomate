import sys
from bs4 import BeautifulSoup

from cloudomate.vps.hoster import Hoster


class SolusvmHoster(Hoster):
    def get_status(self, user_settings):
        raise NotImplementedError('Abstract method implementation')

    def start(self):
        raise NotImplementedError('Abstract method implementation')

    def get_ip(self, user_settings):
        raise NotImplementedError('Abstract method implementation')

    def info(self, user_settings):
        raise NotImplementedError('Abstract method implementation')

    def set_rootpw(self, user_settings):
        raise NotImplementedError('Abstract method implementation')

    def register(self, user_settings, vps_option):
        raise NotImplementedError('Abstract method implementation')

    @staticmethod
    def fill_in_server_form(form, user_settings, rootpw=True, nameservers=True, hostname=True):
        """
        Fills in the form containing server configuration.
        :return: 
        """
        if hostname:
            form['hostname'] = user_settings.get('hostname')
        if rootpw:
            form['rootpw'] = user_settings.get('rootpw')
        if nameservers:
            form['ns1prefix'] = user_settings.get('ns1')
            form['ns2prefix'] = user_settings.get('ns2')
        form.new_control('text', 'ajax', {'name': 'ajax', 'value': 1})
        form.new_control('text', 'a', {'name': 'a', 'value': 'confproduct'})
        form.method = "POST"

    @staticmethod
    def user_form(br, user_settings, payment_method, errorbox_class='checkout-error-feedback', acceptos=True):
        """
        Fills in the form with user information.
        :param errorbox_class: the class of the div containing error messages.
        :param payment_method: the payment method, typically coinbase or bitpay
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
        br.form['state'] = user_settings.get("state")
        br.form['postcode'] = user_settings.get("zipcode")
        br.form['country'] = [user_settings.get('countrycode')]
        br.form['password'] = user_settings.get("password")
        br.form['password2'] = user_settings.get("password")
        br.form['paymentmethod'] = [payment_method]
        if acceptos:
            br.find_control('accepttos').items[0].selected = True

        page = br.submit()
        if 'checkout' in page.geturl():
            contents = BeautifulSoup(page.read(), 'lxml')
            errors = contents.find('div', {'class': errorbox_class}).text
            print(errors.strip())
            sys.exit(2)

    @staticmethod
    def select_form_id(browser, form_id):
        """
        Selects the form with specified id.
        :param browser: the browser
        :param form_id: the form element id
        :return: 
        """
        browser.select_form(predicate=lambda f: 'id' in f.attrs and f.attrs['id'] == form_id)
