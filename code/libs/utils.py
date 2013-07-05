import logging


class DummyDict(dict):

    def getlist(self, key):
        return self[key]

    def parse(self, obj):
        for key in obj:
            self[key] = [obj[key]]
        return self