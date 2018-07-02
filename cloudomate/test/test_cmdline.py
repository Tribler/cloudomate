from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import unittest
from argparse import Namespace

from future import standard_library
from mock.mock import MagicMock

import cloudomate.cmdline as cmdline
from cloudomate.hoster.vpn.azirevpn import AzireVpn
from cloudomate.hoster.vps.linevast import LineVast
from cloudomate.hoster.vps.vps_hoster import VpsOption

standard_library.install_aliases()


class TestCmdLine(unittest.TestCase):
    def setUp(self):
        self.settings_file = os.path.join(os.path.dirname(__file__), 'resources/test_settings.cfg')
        self.vps_options_real = LineVast.get_options
        self.vps_purchase_real = LineVast.purchase

    def tearDown(self):
        LineVast.get_options = self.vps_options_real
        LineVast.purchase = self.vps_purchase_real

    def test_execute_vps_list(self):
        command = ["vps", "list"]
        cmdline.execute(command)

    def test_execute_vpn_list(self):
        command = ["vpn", "list"]
        cmdline.execute(command)

    def test_execute_vps_options(self):
        mock_method = self._mock_vps_options()
        command = ["vps", "options", "linevast"]
        cmdline.providers["vps"]["linevast"].configurations = []
        cmdline.execute(command)
        mock_method.assert_called_once()
        self._restore_vps_options()

    def test_execute_vpn_options(self):
        mock_method = self._mock_vpn_options()
        command = ["vpn", "options", "azirevpn"]
        cmdline.providers["vpn"]["azirevpn"].configurations = []
        cmdline.execute(command)
        mock_method.assert_called_once()
        self._restore_vpn_options()

    def test_execute_vps_purchase(self):
        self._mock_vps_options([self._create_option()])
        purchase = LineVast.purchase
        LineVast.purchase = MagicMock()
        command = ["vps", "purchase", "linevast", "-f", "-c", self.settings_file, "-rp", "asdf", "0"]
        cmdline.execute(command)
        LineVast.purchase.assert_called_once()
        LineVast.purchase = purchase
        self._restore_vps_options()

    @staticmethod
    def _create_option():
        return VpsOption(
            name="Option name",
            memory="Option ram",
            cores="Option cpu",
            storage="Option storage",
            bandwidth="Option bandwidth",
            price=12,
            connection="Option connection",
            purchase_url="Option url"
        )

    def test_execute_vps_purchase_verify_options_failure(self):
        self._mock_vps_options()
        command = ["vps", "purchase", "linevast", "-f", "-c", self.settings_file, "1"]
        self._check_exit_code(1, cmdline.execute, command)
        self._restore_vps_options()

    def test_execute_vps_purchase_unknown_provider(self):
        command = ["vps", "purchase", "nonode", "-f", "-rp", "asdf", "1"]
        self._check_exit_code(2, cmdline.execute, command)

    def test_execute_vps_options_unknown_provider(self):
        command = ["vps", "options", "nonode"]
        self._check_exit_code(2, cmdline.execute, command)

    def _check_exit_code(self, exit_code, method, args):
        try:
            method(args)
        except SystemExit as e:
            self.assertEqual(exit_code, e.code)

    def test_execute_vps_options_no_provider(self):
        command = ["vps", "options"]
        self._check_exit_code(2, cmdline.execute, command)

    def test_purchase_vps_unknown_provider(self):
        args = Namespace()
        args.provider = "sd"
        args.type = "vps"
        self._check_exit_code(2, cmdline.purchase, args)

    def test_purchase_no_provider(self):
        args = Namespace()
        self._check_exit_code(2, cmdline.purchase, args)

    def test_purchase_vps_bad_provider(self):
        args = Namespace()
        args.provider = False
        args.type = "vps"
        self._check_exit_code(2, cmdline.purchase, args)

    def test_purchase_bad_type(self):
        args = Namespace()
        args.provider = "azirevpn"
        args.type = False
        self._check_exit_code(2, cmdline.purchase, args)

    def test_execute_vps_purchase_high_id(self):
        self._mock_vps_options()
        command = ["vps", "purchase", "linevast", "-c", self.settings_file, "-rp", "asdf", "1000"]
        self._check_exit_code(1, cmdline.execute, command)
        self._restore_vps_options()

    def test_execute_vps_purchase_low_id(self):
        mock = self._mock_vps_options()
        command = ["vps", "purchase", "linevast", "-c", self.settings_file, "-rp", "asdf", "-1"]
        self._check_exit_code(1, cmdline.execute, command)
        mock.assert_called_once()
        self._restore_vps_options()

    def _mock_vps_options(self, items=None):
        if items is None:
            items = []
        self.vps_options = LineVast.get_options
        LineVast.get_options = MagicMock(return_value=items)
        return LineVast.get_options

    def _restore_vps_options(self):
        LineVast.get_options = self.vps_options

    def _mock_vpn_options(self, items=None):
        if items is None:
            items = []
        self.vpn_options = AzireVpn.get_options
        AzireVpn.get_options = MagicMock(return_value=items)
        return AzireVpn.get_options

    def _restore_vpn_options(self):
        AzireVpn.get_options = self.vpn_options


if __name__ == '__main__':
    unittest.main(exit=False)
