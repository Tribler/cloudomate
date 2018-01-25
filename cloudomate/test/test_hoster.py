from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest

import requests

from cloudomate.hoster.hoster import Hoster


class TestHosterAbstract(unittest.TestCase):

    def test_create_browser(self):
        browser = Hoster._create_browser()
        if browser.session.headers['user-agent'] == requests.utils.default_user_agent():
            self.fail('No Custom User-agent set in browser')


if __name__ == '__main__':
    unittest.main()
