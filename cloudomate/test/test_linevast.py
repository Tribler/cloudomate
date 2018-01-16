import unittest

from cloudomate.hoster.vps.linevast import LineVast


class TestLinevast(unittest.TestCase):
    def test_check_set_rootpw(self):
        data = '{"success":"1","updtype":"1","apistate":"1"}'
        self.assertTrue(LineVast._check_set_rootpw(data))

    def test_check_set_rootpw_false(self):
        data = '{"success":"1","updtype":"null","apistate":"1"}'
        self.assertFalse(LineVast._check_set_rootpw(data))


if __name__ == '__main__':
    unittest.main(exit=False)
