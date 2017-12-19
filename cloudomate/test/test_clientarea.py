import os
import unittest

from cloudomate.hoster.vps.clientarea import ClientArea
from mock.mock import MagicMock


class TestClientArea(unittest.TestCase):
    def test_emails(self):
        html_file = open(os.path.join(os.path.dirname(__file__), 'resources/clientarea_emails.html'), 'r')
        data = html_file.read()
        html_file.close()
        emails = ClientArea._extract_emails(data)
        self.assertTrue(len(emails) == 5)

    def test_extract_services(self):
        html_file = open(os.path.join(os.path.dirname(__file__), 'resources/clientarea_services.html'), 'r')
        data = html_file.read()
        html_file.close()
        mock = MagicMock(ClientArea)
        mock.clientarea_url = ''
        services = ClientArea._extract_services(mock, data)
        self.assertEqual(services, [
            {'status': 'active', 'product': 'Basic', 'url': '?action=productdetails&id=8961', 'price': '$4.99 USD',
             'term': 'Monthly', 'next_due_date': '2017-06-19', 'id': '8961'},
            {'status': 'cancelled', 'product': 'Basic', 'url': '?action=productdetails&id=9019',
             'price': '$4.99 USD', 'term': 'Monthly', 'next_due_date': '2017-05-24', 'id': '9019'}
        ])

    def test_extract_service(self):
        html_file = open(os.path.join(os.path.dirname(__file__), 'resources/clientarea_service.html'), 'r')
        data = html_file.read()
        html_file.close()
        info = ClientArea._extract_service_info(data)
        self.assertEqual(info, ['hostname', '178.32.53.129', 'ns1.pulseservers.comns2.pulseservers.com'])


if __name__ == '__main__':
    unittest.main(exit=False)
