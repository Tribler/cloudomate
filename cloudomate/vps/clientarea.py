import re
import sys
import time

from bs4 import BeautifulSoup
from flask import json


class ClientArea(object):
    """
    Clientarea is the name of the control panel used in many VPS providers. The purpose of this class is to use
    this control panel in an automated manner.
    """

    def __init__(self, browser, clientarea_url, email, password):
        self.browser = browser
        self.clientarea_url = clientarea_url
        self.home_page = None
        self.services = None
        self._login(email, password)

    def _login(self, email, password):
        """
        Login into the clientarea. Exits program if unsuccesful.
        :return: The clientarea homepage on succesful login.
        """
        self.browser.open(self.clientarea_url)
        self.browser.select_form(nr=0)
        self.browser.form['username'] = email
        self.browser.form['password'] = password
        page = self.browser.submit()
        if "incorrect=true" in page.geturl():
            print("Login failure")
            sys.exit(2)
        self.home_page = page

    def number_of_services(self):
        """
        Return the number of services.
        :return: 
        """
        soup = BeautifulSoup(self.home_page.get_data(), 'lxml')
        stat = soup.find('div', {'class': 'col-sm-3 col-xs-6 tile'}).a.find('div', {'class': 'stat'})
        return stat.text

    def get_services(self):
        """
        Parse and list purchased services from clientarea_url?a=action.
        :return: the list of services in dict format.
        """
        if self.services is None:
            self._services()
        return self.services

    def print_services(self):
        """
        Print parsed VPS configurations.
        """
        self._services()
        row_format = "{:5}" + "{:15}" * 6
        print(row_format.format('#', 'Product', 'Host', 'Price', 'Term', 'Next due date', 'Status', 'Id'))

        i = 0
        for service in self.services:
            print(row_format.format(
                str(i),
                service['product'],
                service['host'],
                service['price'],
                service['term'],
                service['next_due_date'],
                service['status'],
                service['id'],
            ))
            i = i + 1

    def _services(self):
        if self.services is not None:
            return
        services_page = self.browser.open(self.clientarea_url + "?action=services")
        soup = BeautifulSoup(services_page.get_data(), 'lxml')
        rows = soup.find('table', {'id': 'tableServicesList'}).tbody.findAll('tr')
        self.services = []
        for row in rows:
            tds = row.findAll('td', recursive=False)
            self.services.append({
                'id': tds[4].a['href'].split('id=')[1],
                'product': tds[0].strong.text,
                'host': tds[0].a.text,
                'price': tds[1].text.split('USD')[0],
                'term': tds[1].text.split('USD')[1],
                'next_due_date': tds[2].text[0:10],
                'status': tds[3].text,
                'url': self.clientarea_url + tds[4].a['href'].split('.php')[1],
            })

    def _get_vserverid(self, url):
        page = self.browser.open(url)
        match = re.search(r'vserverid = (\d+)', page.get_data())
        return match.group(1)

    def get_ip(self, client_data_url, number=0):
        self._services()
        if not 0 <= number < len(self.services):
            print("Wrong index: %s not between 0 and %s" % (number, len(self.services) - 1))
            sys.exit(2)
        service = self.services[number]
        vserverid = self._get_vserverid(service['url'])
        millis = int(round(time.time() * 1000))
        page = self.browser.open(client_data_url + '?vserverid=%s&_=%s' % (vserverid, millis))
        data = json.loads(page.get_data())
        print(data['mainip'])

    def set_rootpw(self, password, number=0):
        self._services()
        if not 0 <= number < len(self.services):
            print("Wrong index: %s not between 0 and %s" % (number, len(self.services) - 1))
            sys.exit(2)
        service = self.services[number]
        millis = int(round(time.time() * 1000))

        print("Changing password for %s" % service['id'])
        vserverid = self._get_vserverid(service['url'])
        url = self.clientarea_url + '?action=productdetails&id=%s&vserverid=%s&modop=custom&a=ChangeRootPassword' \
                                    '&newrootpassword=%s&ajax=1&ac=Custom_ChangeRootPassword&_=%s' \
                                    % (service['id'], vserverid, password, millis)
        print(url)
        response = self.browser.open(url)
        response_json = json.loads(response.get_data())
        if response_json['success'] is True:
            print("Password changed successfully")
        else:
            print(response_json['msg'])
