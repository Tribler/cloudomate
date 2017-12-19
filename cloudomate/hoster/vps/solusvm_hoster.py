from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
from abc import abstractmethod

from bs4 import BeautifulSoup
from future import standard_library
from mechanicalsoup import LinkNotFoundError

from cloudomate.hoster.vps.clientarea import ClientArea
from cloudomate.hoster.vps.vps_hoster import VpsConfiguration
from cloudomate.hoster.vps.vps_hoster import VpsHoster
from cloudomate.hoster.vps.vps_hoster import VpsStatus
from cloudomate.hoster.vps.vps_hoster import VpsStatusResourceNone

from builtins import super

standard_library.install_aliases()


class SolusvmHoster(VpsHoster):
    """
    SolusvmHoster is the common superclass of all VPS hosters that make use of the Solusvm management package.
    This makes it possible to fill in the registration form in a similar manner for all Solusvm subclasses.
    """

    def __init__(self, settings):
        super().__init__(settings)
        self._clientarea = None

    def _create_clientarea(self):
        if self._clientarea is None:
            self._clientarea = ClientArea(self._browser, self.get_clientarea_url(), self._settings)
        return self._clientarea

    '''
    Methods that are the same for all subclasses
    '''

    def get_configuration(self):
        clientarea = self._create_clientarea()

        ip = clientarea.get_ip()
        password = self._settings.get('server', 'root_password')

        return VpsConfiguration(ip, password)

    def get_status(self):
        clientarea = self._create_clientarea()

        service = clientarea.get_services_first()
        online = True if service.status == 'active' else False
        expiration = service.next_due

        return VpsStatus(
            VpsStatusResourceNone,
            VpsStatusResourceNone,
            VpsStatusResourceNone,
            online,
            expiration,
            service
        )

    '''
    Static methods that must be overwritten by subclasses
    '''

    @staticmethod
    @abstractmethod
    def get_clientarea_url():
        """Get the url of the clientarea for this hoster

        :return: Returns the clientarea url
        """
        pass

    '''
    Methods that are used by subclasses to fill parts of the forms that are shared between hosters
    '''

    def _fill_server_form(self):
        """Fills the server configuration form (should be currently selected) as much as possible

        """
        form = self._browser.get_current_form()

        try:
            form['hostname'] = self._settings.get('server', 'hostname')
        except LinkNotFoundError:
            pass

        try:
            form['rootpw'] = self._settings.get('server', 'root_password')
        except LinkNotFoundError:
            # TODO: Properly handle this warning
            print('Couldn\'t set root password')

        try:
            form['ns1prefix'] = self._settings.get('server', 'ns1')
            form['ns2prefix'] = self._settings.get('server', 'ns2')
        except LinkNotFoundError:
            pass

        # As an alternative to the default Ajax request
        form.new_control('hidden', 'a', 'confproduct')
        form.new_control('hidden', 'ajax', '1')
        form.form['method'] = 'get'

    def _fill_user_form(self, payment_method, errorbox_class='checkout-error-feedback'):
        """Fills the user information form (should be currently selected) as much as possible

        :param payment_method: the name of the payment method
        :param errorbox_class: the class of the div element containing error messages
        :return: the page received after submitted the form
        """
        form = self._browser.get_current_form()

        form['firstname'] = self._settings.get('user', "firstname")
        form['lastname'] = self._settings.get('user', "lastname")
        form['email'] = self._settings.get('user', "email")
        form['phonenumber'] = self._settings.get('user', "phonenumber")
        form['companyname'] = self._settings.get('user', "companyname")
        form['address1'] = self._settings.get('address', "address")
        form['city'] = self._settings.get('address', "city")
        form['state'] = self._settings.get('address', "state")
        form['postcode'] = self._settings.get('address', "zipcode")
        form['country'] = self._settings.get('address', 'countrycode')
        form['password'] = self._settings.get('user', "password")
        form['password2'] = self._settings.get('user', "password")
        form['paymentmethod'] = payment_method.lower()

        try:
            form['accepttos'] = True  # Attempt to accept the terms and conditions
        except LinkNotFoundError:
            pass

        page = self._browser.submit_selected()

        # Error handling
        if 'checkout' in page.url:
            soup = BeautifulSoup(page.text, 'lxml')
            errors = soup.find('div', {'class': errorbox_class}).text
            print((errors.strip()))
            sys.exit(2)

        return page
