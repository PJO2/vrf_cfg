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
#     locate specific data inside the cpe centered structure
#     return an iterable list
# --------------------------------------------------------------------------
def locate_template_specific_data (template, cpe_info):
     with_items = None
     #  specific data are specified in the template database with the with_items keyword
     if 'with_items' in template:
         env = jinja2_env()
         template = env.from_string( '{{ ' + template['with_items'] + ' }}'  )
         output = template.render(cpe=cpe_info)
         with_items = json.loads ( output.replace("'", '"') )     
     return with_items


# --------------------------------------------------------------------------
# execute a template chunk
# may iterate depending on with_items
# --------------------------------------------------------------------------
def render_single_template (tmpl_name, cpe_info, with_items=None):
     """ resolve a single template """
     file_loader = jinja2.FileSystemLoader('templates')   # placeholder for jinja2 templates
     env = jinja2_env(loader=file_loader)
     template = env.get_template( tmpl_name )             # open jinja2 template
     # if with_items is a list iterate on it, give base 1 index
     if isinstance(with_items, list):
        # call constructor first 
        output = template.render(cpe=cpe_info, item=None, index=0)
        # then iterate
        for idx, item in enumerate(with_items, start=1):
            output += template.render(cpe=cpe_info, item=item, index=idx)
     else:
            output = template.render(cpe=cpe_info, item=with_items, index=0) 
     return output


# ---------------------------------------------------------------------------
# Assign a Create, Update, Delete service to a CPE
# ---------------------------------------------------------------------------
def assign_service (service, cpe_info):
     """ generate CPE configuration for a given Service (except read service)

     input:  the cpe centered database, the name of the service
     ouptut: the sums of all templates reltives to the service"""

     config = {}
     # parse the template list for the current role
     for template in cpe_info['role']['templates']:
          # check the template match the service to be applied
          if service in template['services']:
              with_items = locate_template_specific_data(template, cpe_info)
              print ("parsing tempate {}, with_items is {}\tjinja2 rendered with_items is {}".format( 
                                     template['name'], template['with_items'] if 'with_items' in template else '-', with_items) )
              config[template['name']] = render_single_template (template['name'], cpe_info, with_items)
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

