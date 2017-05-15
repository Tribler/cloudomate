import ConfigParser


class Config(object):
    def __init__(self):
        self.config = {}

    def read_config(self, filename="./cloudomate.cfg"):
        cp = ConfigParser.ConfigParser()
        cp.read(filename)
        self._merge(cp.items("User"))
        self._merge(cp.items("Address"))
        self._merge(cp.items("Server"))

    def _merge(self, items):
        for key, value in items:
            self.config[key] = value

    def verify_config(self, options):
        valid = True
        for option in options:
            if option not in self.config:
                print("%s is not in config" % option)
                valid = False
        return valid

    def get(self, key):
        return self.config[key]

    def put(self, key, value):
        self.config[key] = value
