#   Builtin config values: http://flask.pocoo.org/docs/0.10/config/
import os

DEBUG = os.environ.get('DEBUG', False)
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 8080))

LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOGGING_LOCATION = 'front-end.log'
LOGGING_LEVEL = 'DEBUG'

HUBs = [ '10.112.83.100' ]
hub_authent = 'cisco:cisco'
