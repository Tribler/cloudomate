import os
import unittest

from mock.mock import MagicMock

from cloudomate.vps.clientarea import ClientArea


class TestClientArea(unittest.TestCase):
    def test_emails(self):
        html_file = open(os.path.join(os.path.dirname(__file__), 'resources/clientarea_emails.html'), 'r')
        data = html_file.read()
        emails = ClientArea._extract_emails(data)
        self.assertTrue(len(emails) == 5)

    def test_extract_services(self):
        html_file = open(os.path.join(os.path.dirname(__file__), 'resources/clientarea_services.html'), 'r')
        data = html_file.read()
        mock = MagicMock(ClientArea)
        mock.clientarea_url = ''
        services = ClientArea._extract_services(mock, data)
        self.assertEqual(services, [
            {'status': 'active', 'product': u'Basic', 'url': '?action=productdetails&id=8961', 'price': u'$4.99 USD',
             'term': u'Monthly', 'next_due_date': u'2017-06-19', 'id': '8961'},
            {'status': 'cancelled', 'product': u'Basic', 'url': '?action=productdetails&id=9019',
             'price': u'$4.99 USD', 'term': u'Monthly', 'next_due_date': u'2017-05-24', 'id': '9019'}
        ])

    def test_extract_service(self):
        html_file = open(os.path.join(os.path.dirname(__file__), 'resources/clientarea_service.html'), 'r')
        data = html_file.read()
        info = ClientArea._extract_service_info(data)
        self.assertEqual(info, [u'hostname', u'178.32.53.129', u'ns1.pulseservers.comns2.pulseservers.com'])

if __name__ == '__main__':
    unittest.main(exit=False)
