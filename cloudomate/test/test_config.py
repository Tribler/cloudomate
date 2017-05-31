import unittest

from cloudomate.util.config import UserOptions


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config = UserOptions()
        self.config.read_settings("config_test.cfg")

    def test_read_config(self):
        self.assertIsNotNone(self.config)

    def test_has_first_name(self):
        self.assertIsNotNone(self.config.get('firstname'))

    def test_has_email(self):
        self.assertTrue("@" in self.config.get('email'))

    def test_verify_config(self):
        verification = [
            "email",
            "firstname",
            "lastname"
        ]
        self.assertTrue(self.config.verify_options(verification))

    def test_verify_bad_config(self):
        verification = [
            "email",
            "firstname",
            "lastname"
            "randomattribute"
        ]
        self.assertFalse(self.config.verify_options(verification))

    def test_put(self):
        key = "putkey"
        value = "putvalue"
        self.config.put(key, value)
        self.assertEqual(self.config.get(key), value)

    def test_custom_provider(self):
        self.config = UserOptions()
        self.config.read_settings("config_test.cfg", "testhoster")
        self.assertEqual(self.config.get("email"), "test@test.net")

if __name__ == '__main__':
    unittest.main()
