import unittest

from cloudomate.util.config import read_config


class TestConfig(unittest.TestCase):
    def test_has_user(self):
        config = read_config("cloudomate.cfg")
        self.assertIsNotNone("User" in config.sections())

    def test_has_first_name(self):
        config = read_config("cloudomate.cfg")
        self.assertIsNotNone(config.get('User', 'firstName'))

    def test_has_email(self):
        config = read_config("cloudomate.cfg")
        self.assertTrue("@" in config.get('User', 'email'))

    def test_has_address(self):
        config = read_config("cloudomate.cfg")
        self.assertTrue("User" in config.sections())


if __name__ == '__main__':
    unittest.main()
