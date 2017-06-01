import os
import unittest

from cloudomate.vps.crowncloud import CrownCloud


class TestCrownCloud(unittest.TestCase):
    def test_emails(self):
        html_file = open(os.path.join(os.path.dirname(__file__), 'resources/crowncloud_email.html'), 'r')
        data = html_file.read()
        info = CrownCloud._extract_email_info(data)
        self.assertEqual(info, (u'000.000.000.000', u'paneluserxxxx', u'xxxx'))


if __name__ == '__main__':
    unittest.main(exit=False)
