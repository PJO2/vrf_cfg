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
      env = jinja2.Environment(**kwargs)
      env.filters ['ipaddr'] = netaddr_filters.ipaddr      # add netaddr filters (ansible way)
      env.filters ['json_query'] = json_query              # add json_query filter (ansible way)
      return env


# --------------------------------------------------------------------------
# locate specific data inside the cpe centered structure
# return a iterable list
# --------------------------------------------------------------------------
def locate_template_specific_data (template, cpe_info):
     json_vars = None
     #  specific data are specified in the template database with the locator keyword
     if 'with_items' in template:
         env = jinja2_env()
         template = env.from_string( '{{ ' + template['with_items'] + ' }}'  )
         output = template.render(cpe=cpe_info)
         json_vars = json.loads ( output.replace("'", '"') )     
     return json_vars


# --------------------------------------------------------------------------
# execute a template chunk
# may iterate depending on supp_vars
# --------------------------------------------------------------------------
def render_single_template (tmpl_name, cpe_info, supp_vars):
     """ resolve a single template """
     file_loader = jinja2.FileSystemLoader('templates')   # placeholder for jinja2 templates
     env = jinja2_env(loader=file_loader)
     template = env.get_template( tmpl_name )             # open jinja2 template
     if isinstance(supp_vars, list):
        output = ""
        for vars in supp_vars:
            output += template.render(cpe=cpe_info, vars=vars)
     else:
            output = template.render(cpe=cpe_info, vars=supp_vars) 
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
              json_supp_vars = locate_template_specific_data(template, cpe_info)
              print ("parsing tempate {}, locator is {}\njinja2 render vars is {}".
                          format( template['name'], template['with_items'], json_supp_vars) )
              config[template['name']] = render_single_template (template['name'], 
                                                                 cpe_info, 
                                                                 json_supp_vars)
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

