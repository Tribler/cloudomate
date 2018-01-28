from __future__ import absolute_import
from __future__ import division
from __future__ import print_function 
from __future__ import unicode_literals

from builtins import open

import shutil
import requests
import os
import time
import zipfile

from mechanicalsoup import StatefulBrowser
from future import standard_library

from cloudomate.util.settings import Settings

standard_library.install_aliases()

class InstallMullvad(object):
    CONFIGURATION_URL = "https://mullvad.net/en/download/config/"
    TESTING_URL = "https://am.i.mullvad.net/json"

    def __init__(self):
        self._browser = StatefulBrowser(user_agent="Firefox")
        self._settings = Settings()
        self._settings.read_settings()

    def _check_vpn(self, setup=False):
        # Check if VPN is active
        response = requests.get(self.TESTING_URL)
        print(response.json())
       
        # Check if IP's country is Sweden
        if response.json()["country"] == "Sweden":
            print("VPN is active!")
        else:
            if setup:
                print("Error: VPN was not installed!")
            else:
                self.setup_vpn() 

    # Automatically sets up VPN with settings from provider
    def setup_vpn(self):
        # Get the necessary files for connecting to the VPN service
        self._download_files()

        # Copy files to OpenVPN folder
        result = os.popen("sudo cp -a ./config-files/. /etc/openvpn/").read()
        print(result)

        os.chdir("/etc/openvpn/")
     
        # Start OpenVPN connection
        result = os.popen(
        "sudo nohup openvpn --config ./mullvad_se-sto.conf > /dev/null &").read()
        print(result)

        # Sleep for 10 seconds, so that VPN connection can be established in the
        # mean time
        time.sleep(10)
        self._check_vpn(True)

    # Download configuration files for setting up VPN and extract them
    def _download_files(self):
	# Fill information on website to get right files for openVPN
        self._browser.open(self.CONFIGURATION_URL)
        form = self._browser.select_form()
        form["account_token"] = self._settings.get("user", "accountnumber")
        form["platform"] = "linux"
        form["region"] = "se-sto"
        form["port"] = "0"
        self._browser.session.headers["Referer"] = self._browser.get_url()
        response = self._browser.submit_selected()
        content = response.content
        
        # Create the folder that will store the configuration files
        result = os.popen("mkdir config-files").read()
        print(result)

        # Download the zip file to the right location
        files_path = "./config-files/config.zip"
        with open(files_path, "wb") as output:
            output.write(content)

        # Unzip files
        zip_file = zipfile.ZipFile(files_path, "r")
        for member in zip_file.namelist():
            filename = os.path.basename(member)
            # Skip directories
            if not filename:
                continue

            # Copy file (taken from zipfile's extract)
            source = zip_file.open(member)
            target = open(os.path.join("./config-files/", filename), "wb")
            with source, target:
                shutil.copyfileobj(source, target)
        # Delete zip file
        os.remove(files_path)
