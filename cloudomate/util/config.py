import ConfigParser


def read_config(filename="./cloudomate.cfg"):
    cp = ConfigParser.ConfigParser()
    cp.read(filename)
    return cp
