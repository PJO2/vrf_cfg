#!/usr/bin/python3
# -------------------------
# render a template given site data

import jinja2
import json

# jinja2 enlightment
import jmespath
import netaddr_filters

# local files
import device_data

# --------------------------------------------
# Jinja2 hacks  and enlightments
# --------------------------------------------
# need to define a user function to reverse parameter
def json_query(data, expr):
      """Query data into json record using jmespath query language"""
      return jmespath.search(expr, data)

def jinja2_env(**kwargs):
      """ Create a environment for jinja2 """
      env = jinja2.Environment(**kwargs)
      env.filters ['ipaddr'] = netaddr_filters.ipaddr      # add netaddr filters (ansible way)
      env.filters ['json_query'] = json_query              # add json_query filter (ansible way)
      return env


# --------------------------------------------------------------------------
# with_items translation:
#     locate specific data inside the device centered structure
#     return an iterable list
# --------------------------------------------------------------------------
def locate_template_specific_data (template, dev_info):
     with_items = None
     #  specific data are specified in the template database with the with_items keyword
     if 'with_items' in template:
         env = jinja2_env()
         template = env.from_string( '{{ ' + template['with_items'] + ' }}'  )
         output = template.render(device=dev_info)
         with_items = json.loads ( output.replace("'", '"') )     
     return with_items


# --------------------------------------------------------------------------
# execute a template chunk
# may iterate depending on with_items  (may be later with_nested will be implemented)
# --------------------------------------------------------------------------
def render_single_template (tmpl_name, ctor_name, dev_info, with_items=None):
     """ resolve a single template """
     file_loader = jinja2.FileSystemLoader('templates')   # placeholder for jinja2 templates
     env = jinja2_env(loader=file_loader)

     # resolve prolog if present:
     if ctor_name:
          ctor = env.get_template( ctor_name )            # open jinja2 constructor
          output = ctor.render(device=dev_info)            # no user param 
     else:
          output = ""
 
     # and resolve the template itself with iteration on with_items
     template = env.get_template( tmpl_name )             # open jinja2 template
     if isinstance(with_items, list):
        for idx, item in enumerate(with_items, start=1):
            output += template.render(device=dev_info, item=item, index=idx)
     else:
        output += template.render(device=dev_info, item=with_items, index=0) 
     return output


# ---------------------------------------------------------------------------
# Assign a Create, Update, Delete service to a CPE
# ---------------------------------------------------------------------------
def assign_service (service, dev_info):
     """ generate CPE configuration for a given Service (except read service)

     input:  the dev centered database, the name of the service
     ouptut: the sums of all templates reltives to the service"""

     config = {}
     # parse the template list for the current role
     for template in dev_info['templates']:
          # check the template match the service to be applied
          if service in template['services']:
              with_items = locate_template_specific_data(template, dev_info)
              print ("parsing tempate {} prolog {}, with_items is {}\tjinja2 rendered with_items is {}".format( 
                                     template['name'], 
                                     template.get('prolog'), 
                                     template['with_items'] if 'with_items' in template else '-', with_items) )
              config[template['name']] = render_single_template (template['name'], 
                                                                 template.get('prolog'), 
                                                                 dev_info, 
                                                                 with_items)
     return config



if __name__=="__main__":


   import argparse
   import sys

   # retrieve arguments
   parser = argparse.ArgumentParser(epilog = "Example osf use: generate.py -s Limoges001 -r dual1 -v 2 Create")
   parser.add_argument("-s", "--site",      help="The site where the service is to be applied", required=True)
   parser.add_argument("-r", "--role",      help="The topology's role to identify the site device", required=True)
   parser.add_argument("-v", "--verbosity", help="Verbosity level, for troubleshooting", type=int, default=0)
   parser.add_argument("-i", "--instance",  help="The instance number for roles having multiple devices", default=1)
   parser.add_argument("service",  help="The service to apply to a site or device : [Create, Read, Update, Delete]",
                                   choices=['Create', 'Read', 'Update', 'Delete'])
   args = parser.parse_args()
   # retrieve dev centered database
   info = device_data.get_dev_data (args.site, args.role)

   if args.verbosity > 1:
       print ("---------------------------------")
       print(json.dumps( info, sort_keys=False, indent=4, separators=(',', ': ')))
       print ("---------------------------------")
   

   cfg = assign_service (args.service, info)
   for tmpl_name in cfg:
      print("\n\n! ----------------------\n! template {} has returned\n! --------------------------\n{}" . format( tmpl_name, cfg[tmpl_name] ))
 

