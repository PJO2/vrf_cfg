#!/usr/bin/python3
# ------------------------------------------------
# retrieve the site centered information from the database
#   get the site info and attach the following branches
#        - topology
#        - contrat
# The procedure ensure that a topology and a contrat match
# (well actually it does not, but it should be located here)
# ------------------------------------------------

import sys
import yaml

# get the data for a given site
def get_site_data(site_name):

   site_data = {}
   a_yaml_file = open("db.txt")
   db = yaml.load(a_yaml_file, Loader=yaml.FullLoader)

   # find the site
   for site in db['sites']:
     if (site_name == site['name']):
         site_data = site

   # find the matching topology
   for topology in db['topologies']:
      if topology['name'] == site_data['topology']:
         site_data['topology'] = topology

   # find the matching contrat
   for contrat in db['contrats']:
      if contrat['name'] == site_data['contrat']:
         site_data['contrat'] = contrat

   return site_data

if __name__=="__main__":
   info= get_site_data (sys.argv[1])
   print (info)

