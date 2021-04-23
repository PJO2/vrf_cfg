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

#  find a attribute by its name in a dictionnary 
#  ensure that the attribute has been found ans is unique
def find_attribut (attr_name, attr_value, dico):
   branches = [ branch     for  branch in dico[attr_name]   if branch['name'] == attr_value ]
   if len(branches) == 0:
      sys.stderr.write("can not find " + attr_name + " equal to "  + attr_value + " in the database\n")
      raise ValueError ('item not found')
   elif len(branches) > 1:
      sys.stderr.write("multiple "     + attr_name + " equal to "  + attr_value + " have been found in the database\n")
      raise ValueError ('too many items')
   else:
      return branches[0]


def get_cpe_data(site_name, role_name):
   """ retrieve the cpe centered database for a given site and a given role """

   cpe_data = {}
   a_yaml_file = open("db.txt")    # read the databse (actually a single YAML file)
   db = yaml.load(a_yaml_file, Loader=yaml.FullLoader)

   # extract info from the db
   try:
       cpe_data['site']     = find_attribut ('sites',       site_name, db)
       cpe_data['topology'] = find_attribut ('topologies',  cpe_data['site']['topology'],  db)
       cpe_data['contrat']  = find_attribut ('contrats',    cpe_data['site']['contrat'],   db)
       # get the role inside the found topology
       cpe_data['role']     = find_attribut ('roles',       role_name, cpe_data['topology'])
   except:
       pass

   return cpe_data

if __name__=="__main__":
   if len(sys.argv)!=3: 
      print ("Usage: get_cpe_data Site Role")
   else:
      info = get_cpe_data (sys.argv[1], sys.argv[2])
      for sub in info:
         print (sub, "is \n", info[sub], "\n------------------\n")

