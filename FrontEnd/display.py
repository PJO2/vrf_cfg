#!/usr/bin/python3
# --------------------------
# run a display front end
# --------------------------

import os
import flask
import logging
import logging.handlers
import json

# add config 
import config
import restapis
import netconfapis


template_dir = os.path.abspath('html_templates')
frontend = flask.Flask(__name__, template_folder = template_dir)


@frontend.route ("/")
def home():
   return flask.render_template('index.html')

@frontend.route ("/contracts")
def contracts():
   contracts = restapis.build_contracts_list()
   return flask.render_template('contracts.html', contracts=contracts)

@frontend.route ("/contract/<name>")
def contract_info(name):
   contract_info = netconfapis.build_contract_info(name)
   return flask.render_template('contract_info.html', contract=contract_info, contract_id=name)

@frontend.route ("/sites")
def sites():
   sites = restapis.build_sites_list()
   return flask.render_template('sites.html', sites=sites)

@frontend.route ("/site/<name>")
def site_info(name):
   site_info = restapis.build_site_info(name)
   return flask.render_template('site_info.html', site=site_info)


if __name__ == "__main__":
    # Set up logging
    frontend.logger.setLevel(logging.__getattribute__(config.LOGGING_LEVEL))
    file_handler = logging.handlers.RotatingFileHandler(filename=config.LOGGING_LOCATION, maxBytes=10*1024*1024, backupCount=5)
    file_handler.setFormatter(logging.Formatter(config.LOGGING_FORMAT))
    file_handler.setLevel(logging.__getattribute__(config.LOGGING_LEVEL))
    frontend.logger.addHandler(file_handler)
    frontend.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0    # disable caching

    frontend.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
    )
