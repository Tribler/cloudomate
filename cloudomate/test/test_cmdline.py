import unittest
from argparse import Namespace

from mock import patch
from mock.mock import MagicMock

import cloudomate.cmdline as cmdline
from cloudomate.util.config import Config
from cloudomate.vps.scrapy_hoster import ScrapyHoster
from cloudomate.vps.vpsoption import VpsOption


class TestCmdLine(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.config.read_config("config_test.cfg")

    def test_put(self):
        key = "putkey"
        value = "putvalue"
        self.config.put(key, value)
        self.assertEqual(self.config.get(key), value)

    def test_execute_list(self):
        command = ["list"]
        cmdline.execute(command)

    def test_execute_options(self):
        mock_method = self._mock_options()
        command = ["options", "ramnode"]
        cmdline.providers["ramnode"].configurations = []
        cmdline.execute(command)
        mock_method.assert_called_once()

    def test_execute_purchase(self):
        self._mock_options([self._create_option()])
        with patch.object(ScrapyHoster, 'register', return_value=None) as mock_method:
            command = ["purchase", "ramnode", "-rp", "asdf", "0"]
            cmdline.execute(command)
            mock_method.assert_called_once()

    def _create_option(self):
        option = VpsOption()
        option['name'] = "Option name"
        option['virtualization'] = "Option virtualization"
        option['ram'] = "Option ram"
        option['cpu'] = "Option cpu"
        option['ipv4'] = "Option ipv4"
        option['storage'] = "Option storage"
        option['storage_type'] = "Option storage_type"
        option['bandwidth'] = "Option bandwidth"
        option['price'] = "Option price"
        option['location'] = "Option location"
        return option

    def test_execute_purchase_verify_options_failure(self):
        command = ["purchase", "ramnode", "1"]
        self._check_exit_code(2, cmdline.execute, command)

    def test_execute_purchase_unknown_provider(self):
        command = ["purchase", "nonode", "-rp", "asdf", "1"]
        self._check_exit_code(2, cmdline.execute, command)

    def test_execute_options_unknown_provider(self):
        command = ["options", "nonode"]
        self._check_exit_code(2, cmdline.execute, command)

    def _check_exit_code(self, exit_code, method, args):
        try:
            method(args)
        except SystemExit, e:
            self.assertEqual(e.code, exit_code)

    def test_execute_options_no_provider(self):
        command = ["options"]
        self._check_exit_code(2, cmdline.execute, command)

    def test_purchase_unknown_provider(self):
        args = Namespace()
        args.provider = "sd"
        self._check_exit_code(2, cmdline.purchase, args)

    def test_purchase_no_provider(self):
        args = Namespace()
        self._check_exit_code(2, cmdline.purchase, args)

    def test_purchase_bad_provider(self):
        args = Namespace()
        args.provider = False
        self._check_exit_code(2, cmdline.purchase, args)

    def test_execute_purchase_high_id(self):
        self._mock_options()
        command = ["purchase", "ramnode", "-rp", "asdf", "1000"]
        self._check_exit_code(1, cmdline.execute, command)

    def test_execute_purchase_low_id(self):
        mock = self._mock_options()
        command = ["purchase", "ramnode", "-rp", "asdf", "-1"]
        self._check_exit_code(1, cmdline.execute, command)
        mock.assert_called_once()

    def _mock_options(self, items=None):
        if items is None:
            items = []
        ScrapyHoster.options = MagicMock(return_value=items)
        return ScrapyHoster.options


if __name__ == '__main__':
    unittest.main(exit=False)
