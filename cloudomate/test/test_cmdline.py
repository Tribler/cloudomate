import unittest
from argparse import Namespace

import cloudomate.cmdline as cmdline
from cloudomate.hoster.vps.linevast import LineVast
from cloudomate.hoster.vps.vpsoption import VpsOption
from cloudomate.util.config import UserOptions
from mock.mock import MagicMock


class TestCmdLine(unittest.TestCase):
    def setUp(self):
        self.config = UserOptions()
        self.config.read_settings("config_test.cfg")

    def test_put(self):
        key = "putkey"
        value = "putvalue"
        self.config.put(key, value)
        self.assertEqual(self.config.get(key), value)

    def test_execute_list(self):
        command = ["vps", "list"]
        cmdline.execute(command)

    def test_execute_options(self):
        mock_method = self._mock_options()
        command = ["vps", "options", "linevast"]
        cmdline.providers["vps"]["linevast"].configurations = []
        cmdline.execute(command)
        mock_method.assert_called_once()

    def test_execute_purchase(self):
        self._mock_options([self._create_option()])
        LineVast.purchase = MagicMock()
        cmdline._confirmation = MagicMock(return_value=True)
        command = ["vps", "purchase", "linevast", "-f", "-c", "config_test.cfg", "-rp", "asdf", "0"]
        cmdline.execute(command)
        LineVast.purchase.assert_called_once()

    @staticmethod
    def _create_option():
        return VpsOption(
            name="Option name",
            ram="Option ram",
            cpu="Option cpu",
            storage="Option storage",
            bandwidth="Option bandwidth",
            price=12,
            currency="Option currency",
            connection="Option connection",
            purchase_url="Option url"
        )

    def test_execute_purchase_verify_options_failure(self):
        command = ["vps", "purchase", "linevast", "-f", "-c", "config_test.cfg", "1"]
        self._check_exit_code(1, cmdline.execute, command)

    def test_execute_purchase_unknown_provider(self):
        command = ["vps", "purchase", "nonode", "-f", "-rp", "asdf", "1"]
        self._check_exit_code(2, cmdline.execute, command)

    def test_execute_options_unknown_provider(self):
        command = ["vps", "options", "nonode"]
        self._check_exit_code(2, cmdline.execute, command)

    def _check_exit_code(self, exit_code, method, args):
        try:
            method(args)
        except SystemExit as e:
            self.assertEqual(e.code, exit_code)

    def test_execute_options_no_provider(self):
        command = ["vps", "options"]
        self._check_exit_code(2, cmdline.execute, command)

    def test_purchase_unknown_provider(self):
        args = Namespace()
        args.provider = "sd"
        args.type = "vps"
        self._check_exit_code(2, cmdline.purchase, args)

    def test_purchase_no_provider(self):
        args = Namespace()
        self._check_exit_code(2, cmdline.purchase, args)

    def test_purchase_bad_provider(self):
        args = Namespace()
        args.provider = False
        args.type = "vps"
        self._check_exit_code(2, cmdline.purchase, args)

    def test_execute_purchase_high_id(self):
        self._mock_options()
        command = ["vps", "purchase", "linevast", "-c", "config_test.cfg", "-rp", "asdf", "1000"]
        self._check_exit_code(1, cmdline.execute, command)

    def test_execute_purchase_low_id(self):
        mock = self._mock_options()
        command = ["vps", "purchase", "linevast", "-c", "config_test.cfg", "-rp", "asdf", "-1"]
        self._check_exit_code(1, cmdline.execute, command)
        mock.assert_called_once()

    @staticmethod
    def _mock_options(items=None):
        if items is None:
            items = []
        LineVast.options = MagicMock(return_value=items)
        return LineVast.options


if __name__ == '__main__':
    unittest.main(exit=False)
