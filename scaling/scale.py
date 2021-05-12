#!/usr/bin/python3
# ---------------------
# create 2000 peers on the RS
# --------------------

import random
import string
import jinja2

random.seed(100)    # fix strings generation

CreateContract = """
ip extcommunity-list standard Contract_{{ contract.id }} permit rt {{ contract.id }}
"""

CreateSite = """
int loopback 100
   ip address 172.19.{{ site.id // 100}}.{{ site.id % 100}} 255.255.255.255 secondary


{% for vrf in vrfs  %}
route-map From_{{ site.name }} permit {{ vrf.id }}
  description -- Site is {{ site.name }}, vrf {{ vrf.name }} --
  match extcommunity vrf_{{ vrf.name }}
  set extcommunity rt 65000:{{ vrf.id }} 65500:{{ contract.id }} additive
{% endfor %}

route-map To_{{ site.name }} permit {{ contract.id }}
   description -- site is {{ site.name }} }}, contract is {{ contract.name }} --
   match extcommunity {{ contract.id }}

router bgp 65500
      neighbor 172.20.{{ site.id // 100}}.{{ site.id % 100}} inherit peer-session CEs

   address-family vpnv4
      neighbor 172.20.{{ site.id // 100}}.{{ site.id % 100}} activate
      neighbor 172.20.{{ site.id // 100}}.{{ site.id % 100}} inherit peer-policy CEs
      neighbor 172.20.{{ site.id // 100}}.{{ site.id % 100}} route-map From_{{ site.name }} in
      neighbor 172.20.{{ site.id // 100}}.{{ site.id % 100}} route-map To_{{ site.name }} out

"""

vrfs = [  { "name": "Data1", "id": 31 }, { "name": "Video", "id": 41 }, { "name": "Phone", "id": 46 } ]
contract = { "name": "contract", "id": 0 }
letters = string.ascii_lowercase


# Create 100 contract
for ark in range (500, 601):
   template = jinja2.Template(CreateContract)
   contract['id'] = ark
   output = template.render (contract=contract)
   print (output)

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


