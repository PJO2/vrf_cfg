#!/usr/bin/python3
# ---------------------
# create a Gobgp.config file to handle 1000's peers
# ------------------------

import jinja2
import string
import random
import sys

letters = string.ascii_lowercase

prolog = """
[global.config]
as = 65000
router-id = "10.112.83.105"
# to disable listening
port = -1


[[peer-groups]]
  [peer-groups.config]
    peer-group-name = "scaling-group"
    peer-as = 65500
  [[peer-groups.afi-safis]]
    [peer-groups.afi-safis.config]
      afi-safi-name = "l3vpn-ipv4-unicast"
  [peer-groups.ebgp-multihop.config]
    enabled = true
    multihop-ttl = 50
  [peer-groups.as-path-options.config]
    allow-own-as = 1

"""

peer_cfg = '''
[[neighbors]]
    [neighbors.config]
        neighbor-address = "172.19.{{ site.id // 100}}.{{ site.id % 100}}"
        peer-group = "scaling-group"
    [neighbors.transport.config]
        local-address = "172.20.{{ site.id // 100}}.{{ site.id % 100}}"

'''


print (prolog)
for ark in range (int (sys.argv[1]), int (sys.argv[2])):
   site = {}
   site['name']   = ''.join(random.choice(letters) for i in range(10))
   site['id']     = ark
   # resolve template
   template = jinja2.Template(peer_cfg)
   output = template.render (site=site)
   print (output)


