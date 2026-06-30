__author__ = 'ivand'

import yaml

try:
    from yaml import CLoader as Loader, CDumper
except ImportError:
    from yaml import Loader, Dumper


class ReadConfig(object):
    def __init__(self, cfg_file):
        in_stream = open(cfg_file, 'r')
        self.data = yaml.load(in_stream, Loader=yaml.FullLoader)

    def getsections(self):
        return list(self.data.keys())

    def getsection(self, section):
        return self.data[section]
