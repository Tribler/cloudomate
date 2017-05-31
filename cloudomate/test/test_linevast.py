import unittest

from mechanize import Link

from cloudomate.vps.linevast import LineVast


class TestLinevast(unittest.TestCase):
    def test_execute_purchase_low_id(self):
        links = [
            Link(base_url='https://vm.linevast.de/home.php', url='home.php', text='Linevast Servers', tag='a',
                 attrs=[('class', 'brand'), ('href', 'home.php')]),
            Link(base_url='https://vm.linevast.de/home.php', url='home.php', text='Home', tag='a',
                 attrs=[('href', 'home.php')]),
            Link(base_url='https://vm.linevast.de/home.php', url='home.php', text='Virtual Servers', tag='a',
                 attrs=[('href', 'home.php')]),
            Link(base_url='https://vm.linevast.de/home.php', url='dns.php', text='DNS', tag='a',
                 attrs=[('href', 'dns.php')]),
            Link(base_url='https://vm.linevast.de/home.php', url='https://panel.linevast.de/index.php?m=RFW_Installer',
                 text='Auto Installer', tag='a',
                 attrs=[('href', 'https://panel.linevast.de/index.php?m=RFW_Installer')]),
            Link(base_url='https://vm.linevast.de/home.php', url='https://panel.linevast.de/', text='Customer Panel',
                 tag='a', attrs=[('href', 'https://panel.linevast.de/')]),
            Link(base_url='https://vm.linevast.de/home.php', url='account.php', text='My Account', tag='a',
                 attrs=[('href', 'account.php')]),
            Link(base_url='https://vm.linevast.de/home.php', url='https://panel.linevast.de/', text='Support', tag='a',
                 attrs=[('href', 'https://panel.linevast.de/')]),
            Link(base_url='https://vm.linevast.de/home.php', url='logout.php', text='Logout', tag='a',
                 attrs=[('href', 'logout.php')]),
            Link(base_url='https://vm.linevast.de/home.php', url='control.php?_v=a4x2x2c4o2i5s29403v2',
                 text='qrv5z0g.server.linevast.org', tag='a', attrs=[('href', 'control.php?_v=a4x2x2c4o2i5s29403v2')]),
            Link(base_url='https://vm.linevast.de/home.php', url='http://www.solusvm.com', text='SolusVM', tag='a',
                 attrs=[('href', 'http://www.solusvm.com'), ('title', 'visit solusvm.com'), ('target', '_blank')])
        ]
        vi = LineVast._extract_vi_from_links(links)
        self.assertEqual(vi, "a4x2x2c4o2i5s29403v2")

    def test_check_set_rootpw(self):
        data = '{"success":"1","updtype":"1","apistate":"1"}'
        self.assertTrue(LineVast._check_set_rootpw(data))

    def test_check_set_rootpw_false(self):
        data = '{"success":"1","updtype":"null","apistate":"1"}'
        self.assertFalse(LineVast._check_set_rootpw(data))

if __name__ == '__main__':
    unittest.main(exit=False)
