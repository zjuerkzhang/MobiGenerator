import logging
import os

selfDir = os.path.dirname(os.path.abspath(__file__))
fileName = '.'.join(__file__.split('.')[:-1]).split('/')[-1]
logFilePath = ("%s/../log/%s.log" % (selfDir, fileName))
FORMAT = '%(asctime)s %(name)s [%(levelname)s]: %(message)s'
DATEFMT = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(filename = logFilePath, level = logging.DEBUG, format = FORMAT, datefmt = DATEFMT)

class MyLogger(object):
    @classmethod
    def getLogger(cls, identifier):
        return logging.getLogger(identifier)