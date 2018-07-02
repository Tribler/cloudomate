from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import open
from builtins import str
from configparser import ConfigParser
from configparser import NoOptionError

from appdirs import *
from future import standard_library

standard_library.install_aliases()


class Settings(object):
    def __init__(self):
        self.settings = ConfigParser()
        config_dir = user_config_dir()
        self._default_filename = os.path.join(config_dir, 'cloudomate.cfg')

    def get_default_config_location(self):
        return self._default_filename

    def read_settings(self, filename=None):
        """Read the settings object from a file.

        If the filename is omitted it is read from the default <user_config_dir>/cloudomate.conf location.

        :param filename: The file to read it from
        :return: Whether or not the config was successfully read
        """
        if not filename:
            filename = self._default_filename

        if not os.path.exists(filename):
            print("Config file: '%s' not found" % filename)
            return False
        files = self.settings.read(filename, encoding='utf-8')
        return len(files) > 0

    def save_settings(self, filename=None):
        """Save this settings object to a file.

        If the filename is omitted it is saved to the default <user_config_dir>/cloudomate.conf location.

        :param filename: The file to save it to
        :return: Whether or not the config was successfully written
        """
        if not filename:
            filename = self._default_filename

        try:
            self.settings.write(open(filename, 'w', encoding='utf-8'))
        except IOError:
            print("Failed to write configuration to '{}', printing it to stdout:".format(filename), file=sys.stderr)
            self.settings.write(sys.stdout)

    def verify_options(self, options):
        valid = True
        for section, keys in options.items():
            if not self.settings.has_section(section):
                print("Section {} does not exist".format(section))
                valid = False
            else:
                for key in keys:
                    if not self.settings.has_option(section, key):
                        print("Setting {}.{} does not exist".format(section, key))
                        valid = False
        return valid

    def get(self, section, key):
        return self.settings.get(section, key)

    def get_merge(self, sections, key):
        """Get a value from a merge of specified sections.
        The order of the passed sections denote their priority with the first having the highest priority.
        :param sections: The sections to look in for the value
        :param key: The key of the setting
        :return: The desired settings value
        """
        for section in sections:
            if self.settings.has_option(section, key):
                return self.settings.get(section, key)
        print("Setting {} does not exist in any of the given sections".format(key))
        raise NoOptionError(sections[-1], key)

    def put(self, section, key, value):
        if not self.settings.has_section(section):
            self.settings.add_section(section)

        self.settings.set(section, key, str(value))

    def has_key(self, section, key):
        return self.settings.has_option(section, key)

    def has_key_merge(self, sections, key):
        for section in sections:
            if self.settings.has_option(section, key):
                return True
        raise False
