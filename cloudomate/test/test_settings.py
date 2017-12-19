from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest

import os
from future import standard_library

from cloudomate.util.settings import Settings

standard_library.install_aliases()


class TestSettings(unittest.TestCase):
    def setUp(self):
        self.settings = Settings()
        self.settings.read_settings(os.path.join(os.path.dirname(__file__), 'resources/test_settings.cfg'))

    def test_read_config(self):
        self.assertIsNotNone(self.settings)

    def test_has_first_name(self):
        self.assertIsNotNone(self.settings.get('user', 'firstname'))

    def test_has_email(self):
        self.assertTrue("@" in self.settings.get('user', 'email'))

    def test_verify_config(self):
        verification = {
            "user": [
                "email",
                'firstname',
                'lastname'
            ]
        }
        self.assertTrue(self.settings.verify_options(verification))

    def test_verify_bad_config(self):
        verification = {
            "user": [
                "email",
                'firstname',
                'lastname'
                "randomattribute"
            ]
        }
        self.assertFalse(self.settings.verify_options(verification))

    def test_put(self):
        key = "putkey"
        section = "putsection"
        value = "putvalue"
        self.settings.put(section, key, value)
        self.assertEqual(self.settings.get(section, key), value)

    def test_get_merge(self):
        key = 'email'
        sections = ['testhoster', 'user']
        value = 'test@test.net'
        self.assertEqual(self.settings.get_merge(sections, key), value)

    def test_get_merge_ordering(self):
        key = 'email'
        sections = ['user', 'testhoster']
        value = 'bot@pleb.net'
        self.assertEqual(self.settings.get_merge(sections, key), value)

    def test_custom_provider(self):
        self.assertEqual(self.settings.get("testhoster", "email"), "test@test.net")


if __name__ == '__main__':
    unittest.main()
