import ConfigParser
from ConfigParser import NoSectionError

from appdirs import *


class UserOptions(object):
    def __init__(self):
        self.config = {}

    def read_settings(self, filename=None, provider=None):
        cp = ConfigParser.ConfigParser()
        if not filename:
            config_dir = user_config_dir()
            filename = os.path.join(config_dir, 'cloudomate.cfg')

        if not os.path.exists(filename):
            print("cloudomate.cfg not found at %s" % filename)
            return False
        cp.read(filename)
        try:
            self._merge(cp, "User")
            self._merge(cp, "Address")
            self._merge(cp, "Server")
            if provider:
                self._merge(cp, provider)
        except NoSectionError, e:
            print(e.message)
            return False
        return True

    def _merge(self, cp, section):
        if section not in cp.sections():
            return
        for key, value in cp.items(section):
            self.config[key] = value

    def verify_options(self, options):
        valid = True
        for option in options:
            if option not in self.config or not self.config.get(option):
                print("%s is not in config" % option)
                valid = False
        return valid

    def get(self, key):
        return self.config[key]

    def put(self, key, value):
        self.config[key] = value
