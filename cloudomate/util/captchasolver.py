import json
import requests
import time
import os
import base64

"""
Usage: 

Feed Anti Captcha account API key to solver:
c_solver = CaptchaSolver("fd58e13e22604e820052b44611d61d6c")

Find out how much money is left:
temp = c_solver.get_balance()

Provide captcha image full path to solver method to get solution:
solution = c_solver.solve_captcha_text_case_sensitive(
                     "/home/testm2/Desktop/testcscr/php/pyhton/cap2.jpg")
print(str(solution))

Feed Anti-captcha account API key to solver:
rc_solver = ReCaptchaSolver("fd58e13e22604e820052b44611d61d6c")

Find out how much money is left:
temp = rc_solver.get_balance()

Provide solver method with Google ReCapthca URL and ReCaptcha website
key usually found as data-sitekey attribute in an HTML element in the
website containing the ReCaptcha:
wUrl = "http://http.myjino.ru/recaptcha/test-get.php"
wKey = "6Lc_aCMTAAAAABx7u2W0WPXnVbI_v6ZdbM6rYf16"
rc_solution = rc_solver.solve_google_recaptcha(wUrl,wKey)
print(rc_solution)
"""


class CaptchaSolver(object):

    _client_key = "not set"
         
    def __init__(self, c_key):
        self._client_key = c_key

    def get_balance(self):
        # Query API for account balance
        response = requests.post("https://api.anti-captcha.com/getBalance",
                                 json={"clientKey": self._client_key})

        # Check response of HTTP request
        if (response.status_code == requests.codes.ok):
            response_json = json.loads(response.text)
            if (response_json["errorId"] == 0):
                print("Successful, account balance returned")
                return response_json["balance"]
            else:
                # Print API error
                print(response.text)
        else:
            # Print request error
            print(response.status_code)

    def solve_captcha_text_case_sensitive(self, full_image_file_path):
        # Encode captcha image before sending it
        encoded_image_string = ""
        if os.path.isfile(full_image_file_path):
            with open(full_image_file_path, "rb") as image_file:
                encoded_image_string = base64.b64encode(image_file.read())
                print("Captcha image sucessfully encoded")
        else:
            print("Error: file path not found")
            return

        # Create new Captcha solving task using the API
        task_id = self._create_task_captcha_text_case_sensitive(
                         encoded_image_string)
        
        # Query API until task is finished
        current_status = self._get_task_status(task_id)
        while current_status == "processing":
            print("Sleeping 5 sec")
            time.sleep(5)
            current_status = self._get_task_status(task_id)
            print("Current status: " + str(current_status))

        # Get solution
        solution = self._get_task_result(task_id)
        return solution["text"]
           
    def _get_task_result(self, task_id):
        # Query API for the solution of the task       
        response = requests.post("https://api.anti-captcha.com/getTaskResult",
                                 json={"clientKey": self._client_key,
                                 "taskId": task_id})

        # Check response of HTTP request
        if (response.status_code == requests.codes.ok):
            response_json = json.loads(response.text)
            if (response_json["errorId"] == 0):
                print("Successful, captcha solved:")
                return response_json["solution"]
            else:
                # Print API error
                print(response.text)
        else:
            # Print request error
            print(response.status_code)

    def _get_task_status(self, task_id):
        # Query API for the status of the task
        response = requests.post("https://api.anti-captcha.com/getTaskResult",
                                 json={"clientKey": self._client_key,
                                 "taskId": task_id})

        # Check response of HTTP request
        if (response.status_code == requests.codes.ok):
            response_json = json.loads(response.text)
            if (response_json["errorId"] == 0):
                print("Successful, task status returned")
                return response_json["status"]
            else:
                # Print API error
                print(response.text)
        else:
            # Print request error
            print(response.status_code)

    def _create_task_captcha_text_case_sensitive(self, base64_image_string):
        # Send task creation command to API
        response = requests.post("https://api.anti-captcha.com/createTask",
                                 json={"clientKey": self._client_key,
                                 "task":
                                 {
                                  "type": "ImageToTextTask",
                                  "body": base64_image_string,
                                  "phrase": False,
                                  "case": True,
                                  "numeric": False,
                                  "math": 0,
                                  "minLength": 0,
                                  "maxLength": 0
                                 }
                                 })

        # Check response of HTTP request
        if (response.status_code == requests.codes.ok):
            response_json = json.loads(response.text)
            if (response_json["errorId"] == 0):
                print("Successful, captcha task was created:" + response.text)
                return response_json["taskId"]
            elif (response_json["errorCode"] == "ERROR_NO_SLOT_AVAILABLE"):
                time.sleep(15)
                return self._create_task_captcha_text_case_sensitive(
                              base64_image_string)
            else:
                # Print API error
                print(response.text)
        else:
            # Print request error
            print(response.status_code)

    def get_current_key(self):
        return self._client_key


class ReCaptchaSolver(CaptchaSolver):


    def _create_task_google_recaptcha(self, website_url, website_key):
        # Send task creation command to API
        response = requests.post("https://api.anti-captcha.com/createTask",
                                 json={"clientKey": self._client_key, "task":
                                 {
                                  "type": "NoCaptchaTaskProxyless",
                                  "websiteURL": website_url,
                                  "websiteKey": website_key
                                 },
                                  "softId": 0,
                                  "languagePool": "en"
                                 })

        # Check response of HTTP request
        if (response.status_code == requests.codes.ok):
            response_json = json.loads(response.text)
            if (response_json["errorId"] == 0):
                print("Successful, task was created: " + response.text)
                return response_json["taskId"]
            elif (response_json["errorCode"] == "ERROR_NO_SLOT_AVAILABLE"):
                # In case task could not be created, create it again
                time.sleep(15)
                return self._create_task_google_recaptcha(website_url, 
                                                           website_key)
            else:
                # Print API errordd
                print(response.text)
        else:
            # Print request error
            print(response.status_code)

    def solve_google_recaptcha(self, website_url, website_key):
        # Create new Google ReCaptcha solving task using the API
        task_id = self._create_task_google_recaptcha(website_url, website_key)
        print("Sleeping 15 sec")
        time.sleep(15)

        # Query API until task is finished
        current_status = self._get_task_status(task_id)
        while current_status == "processing":
            print("Current status: " + str(current_status))
            print("Sleeping 5 sec")
            time.sleep(5)
            current_status = self._get_task_status(task_id)
            print("Current status: " + str(current_status))

        # Get solution of task
        solution = self._get_task_result(task_id)
        return solution["gRecaptchaResponse"]
