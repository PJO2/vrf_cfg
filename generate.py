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
def locate_template_iteration_data (template, dev_info):
     with_items = None
     #  specific data are specified in the template database with the with_items keyword
     if 'with_items' in template:
         env = jinja2_env()
         template = env.from_string( '{{ ' + template['with_items'] + ' }}'  )
         output = template.render(device=dev_info)
         with_items = json.loads ( output.replace("'", '"') )     
     return with_items

# --------------------------------------------------------------------------
# with_extra translation:
#     locate specific data inside the device centered structure
# --------------------------------------------------------------------------
def locate_template_specific_data (extra_expr, dev_info, item):
     extra = None
     #  specific data are specified in the template database with the with_items keyword
     if extra_expr:
         env = jinja2_env()
         template = env.from_string( '{{ ' + extra_expr + ' | first  }}'  )
         output = template.render(device=dev_info, item=item)
         extra = json.loads ( output.replace("'", '"') )     
     return extra


# --------------------------------------------------------------------------
# execute a template chunk
# may iterate depending on with_items  (may be later with_nested will be implemented)
# --------------------------------------------------------------------------
def render_single_template (tmpl_name, ctor_name, extra_expr, dev_info, with_items=None):
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
            extra = locate_template_specific_data(extra_expr, dev_info, item)
            output += template.render(device=dev_info, item=item, index=idx, extra=extra)
     else:
        extra = locate_template_specific_data(extra_expr, dev_info, None)
        output += template.render(device=dev_info, item=None, index=0, extra=extra) 
     return output


# ---------------------------------------------------------------------------
# Assign a Create, Update, Delete service to a CPE
# ---------------------------------------------------------------------------
def assign_service_debug(template, with_items):
    print ("parsing tempate {} prolog {}, extra {}, with_items is {}\tjinja2 rendered with_items is {}".format( 
                    template['file'], 
                    template.get('prolog'), 
                    template['with_extra'] if 'with_extra' in template else 'None',
                    template['with_items'] if 'with_items' in template else 'None', 
                    with_items) )



def assign_service (service, dev_info):
     """ generate CPE configuration for a given Service (except read service)

     input:  the dev centered database, the name of the service
     ouptut: the sums of all templates reltives to the service"""

     config_tmpl = {}
     config_lines = ""
     templates = sorted( dev_info['templates'], key=lambda tmpl: tmpl.get('precedence', 100) )
     # parse the template list for the current role
     for template in templates:
          # check the template match the service to be applied
          if service in template['services']:
              # provide the template entry to the device centered variable
              dev_info['template'] = template
              with_items = locate_template_iteration_data(template, dev_info)
              assign_service_debug(template, with_items)    # some debugs
              config_tmpl[template['name']] = render_single_template (template['file'], 
                                                                 template.get('prolog'), 
                                                                 template.get('with_extra'), 
                                                                 dev_info, 
                                                                 with_items)
              config_lines += config_tmpl[template['name']] + "\n"
     return (config_lines, config_tmpl)



if __name__=="__main__":


   import argparse
   import sys

   # retrieve arguments
   parser = argparse.ArgumentParser(epilog = "Example of use: ./generate.py -s Limoges001 -r dual1 -v 2 Create")
   parser.add_argument("-s", "--site",      help="The site where the service is to be applied", required=True)
   parser.add_argument("-r", "--role",      help="The topology's role to identify the site device", required=True)
   parser.add_argument("-v", "--verbosity", help="Verbosity level, for troubleshooting", type=int, default=0)
   parser.add_argument("-i", "--instance",  help="The instance number for roles having multiple devices", default=1)
   parser.add_argument("-o", "--output",    help="The file to be written with the device configuration")
   parser.add_argument("service",  help="The service to apply to a site or device : [Create, Read, Update, Delete]",
                                   choices=['Create', 'Read', 'Update', 'Delete'])
   args = parser.parse_args()
   # retrieve dev centered database
   info = device_data.get_dev_data (args.site, args.role)

   if args.verbosity > 1:
       print ("---------------------------------")
       print(json.dumps( info, sort_keys=False, indent=4, separators=(',', ': ')))
       print ("---------------------------------")
   

   cfg_lines, cfg_templ = assign_service (args.service, info)
   for tmpl_name in cfg_templ:
      print("\n\n! ----------------------\n! template {} has returned\n! --------------------------\n{}" . format( tmpl_name, cfg_templ[tmpl_name] ))

   # write templates sorted by precedence
   if args.output: 
      with open(args.output, "w") as file_object:
           file_object.write( cfg_lines )

