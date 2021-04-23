#!/usr/bin/python3
# -------------------------
# render a template given site data

import jinja2
import json
import sys

# jinja2 enlightment
import jmespath
import netaddr_filters

# local files
import get_cpe_data

# need to define a user function to reverse parameter
def json_query(data, expr):
      """Query data into json record using jmespath query language"""
      return jmespath.search(expr, data)

def render_per_vrf_template (tmpl_name, cpe_info, site_vrf_vars):
     """ resolve a single template """
     file_loader = jinja2.FileSystemLoader('templates')   # placeholder for jinja2 templates
     env = jinja2.Environment(loader=file_loader)
     env.filters ['ipaddr'] = netaddr_filters.ipaddr      # add netaddr filters (ansible way)
     env.filters ['json_query'] = json_query              # add json_query filter (ansible way)
     template = env.get_template(tmpl_name + '.j2')       # open jinja2 template
     output = template.render(cpe=cpe_info, vrf=site_vrf_vars)      # and convert it

     return output


# Assign a Create, Update, Delete service to a CPE
def assign_service (service, cpe_info):
     """ generate CPE configuration for a given Service (except read service)

     input:  the cpe centered database, the name of the service
     ouptut: the sums of all templates reltives to the service"""

     config = {}
     for vrf in cpe_info['topology']['vrfs']:
         for template in vrf['templates']:
             if service in template['services']:
                site_vrf_vars = get_cpe_data.find_attribut ('vrfs', vrf['name'], cpe_info['site']['vars'])
                config[template['name']] = render_per_vrf_template (template['name'], 
                                                                   cpe_info, 
                                                                   site_vrf_vars)
     return config



if __name__=="__main__":
   if len(sys.argv) != 4:
      print ("Usage: generate_config Service Site Role")
      quit()

   # retrieve arguments
   service, site_name, role_name = sys.argv[1:4]
   # retrieve cpe centered database
   info = get_cpe_data.get_cpe_data (site_name, role_name)

   print ("---------------------------------")
   print(json.dumps( info, sort_keys=False, indent=4, separators=(',', ': ')))
   print ("---------------------------------")
   

   cfg = assign_service (service, info)
   for tmpl_name in cfg:
      print("template {} has returned\n{}\n----\n" . format( tmpl_name, cfg[tmpl_name] ))

