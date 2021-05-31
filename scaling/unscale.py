#!/usr/bin/python3
# ---------------------
# create 2000 peers on the RS
# --------------------

import random
import string
import jinja2

random.seed(100)    # fix strings generation

CreateSite = """
int loopback 100
   no ip address 172.19.{{ site.id // 100}}.{{ site.id % 100}} 255.255.255.255 secondary
"""

vrfs = [  { "name": "Data1", "id": 31 }, { "name": "Video", "id": 41 }, { "name": "Phone", "id": 46 } ]
contract = { "name": "contract", "id": 0 }
letters = string.ascii_lowercase


# create 2000 peers
for ark in range (201, 4000):
   contract['id'] = random.randint(500, 600)
   site = {}
   site['name']   = ''.join(random.choice(letters) for i in range(10))
   site['id']     = ark
   # resolve template
   template = jinja2.Template(CreateSite)
   output = template.render (site=site, vrfs=vrfs, contract=contract)
   print (output)

print ("\nend\n")


