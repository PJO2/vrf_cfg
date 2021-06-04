# ---------------------------------------
# netconf API 
# ---------------------------------------

import xmltodict
import json

def y():
    infile = open('get_all.xml', 'r')
    content = infile.read()
    c = xmltodict.parse (content)
    # build the list
    print ( json.dumps (c, indent=4) )

y() 
