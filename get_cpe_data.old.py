#!/usr/bin/python3
# ------------------------------------------------
# retrieve the cpe centered information from the database
#   get the site info and attach the following branches
#        - topology
#        - contrat
#        - role
# The procedure ensure that a topology/contrat/role match
# (well actually it does not, but it should be located here)
# ------------------------------------------------

import sys
import yaml

# get the data for a given site
def get_cpe_data(site_name, role_name):

   cpe_data = {}
   a_yaml_file = open("db.txt")
   db = yaml.load(a_yaml_file, Loader=yaml.FullLoader)

   # find the site
   sites = [ site    for site in db['sites']   if site_name == site['name']]
   if len(sites)!=1:
      sys.stderr.write("can not find site " + site_name + " in the database\n")
      return -1
   cpe_data['site'] = sites [0]

   # find the matching topology
   topologies = [ topology   for topology in db['topologies']   if topology['name'] == cpe_data['site']['topology']]
   if len(topologies)!=1:
      sys.stderr.write("can not find topology " + cpe_data['site']['topology'] + " in the database\n")
      return -1
   cpe_data['topology'] = topologies[0]

   # find the matching contrat
   contrats = [ contrat    for contrat in db['contrats']    if contrat['name'] == cpe_data['site']['contrat']]
   if len(contrats)!=1:
      sys.stderr.write("can not find contrat " + cpe_data['site']['contrat'] + " in the database\n")
      return -1
   cpe_data['contrat'] = contrats[0]
 
   # recurse into the topology to find the role
   roles = [ role   for role in cpe_data['topology']['roles']     if role['name'] == role_name ]
   if len(roles)!=1:
      sys.stderr.write("can not find contrat " + cpe_data['topology']['roles']['name']  + " in the database\n")
      return -1
   cpe_data['role'] = roles[0]

   return cpe_data

if __name__=="__main__":
   if len(sys.argv)!=3: 
      print ("Usage: get_cpe_data Site Role")
   else:
      info= get_cpe_data (sys.argv[1], sys.argv[2])
      for sub in [ 'site', 'topology', 'contrat']:
         print (sub, "is \n", info[sub], "\n------------------\n")

