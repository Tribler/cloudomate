import unittest
import time
import os

from cloudomate.util.captchasolver import CaptchaSolver, ReCaptchaSolver
from mock import patch, MagicMock


class TestCaptchaSolver(unittest.TestCase):

    def setUp(self):
        self.captcha_solver = CaptchaSolver("213389asd8u912823")
        self.recaptcha_solver = ReCaptchaSolver("213389asd8u912824")

    def test_get_current_key(self):
        self.assertEqual(self.captcha_solver.get_current_key(),"213389asd8u912823")
        self.assertEqual(self.recaptcha_solver.get_current_key(),"213389asd8u912824")

    @patch("time.sleep")
    def test_solve_captcha_text_case_sensitive(self, mock_time):
        self.captcha_solver._create_task_captcha_text_case_sensitive = MagicMock()
        self.captcha_solver._get_task_status = MagicMock()
        self.captcha_solver._get_task_result = MagicMock()
         
        
        self.captcha_solver.solve_captcha_text_case_sensitive(os.path.join(os.path.dirname(__file__),"resources/captcha.png"))

        self.assertTrue(self.captcha_solver._create_task_captcha_text_case_sensitive.called)
        self.assertTrue(self.captcha_solver._get_task_status.called)
        self.assertTrue(self.captcha_solver._get_task_result.called)

    @patch("time.sleep")
    def test_solve_google_recaptcha(self, mock_time):
        self.recaptcha_solver._create_task_google_recaptcha = MagicMock()
        self.recaptcha_solver._get_task_status = MagicMock()
        self.recaptcha_solver._get_task_result = MagicMock()
         
        self.recaptcha_solver.solve_google_recaptcha("test1","test2")

        self.assertTrue(self.recaptcha_solver._create_task_google_recaptcha.called)
        self.assertTrue(self.recaptcha_solver._get_task_status.called)
        self.assertTrue(self.recaptcha_solver._get_task_result.called)


if __name__ == "__main__":
    unittest.main()
