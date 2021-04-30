#!/usr/bin/python3
# ------------------------------------------------
# retrieve the device centered information from the database
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


def get_dev_data(site_name, role_name):
   """ retrieve the cpe centered database for a given site and a given role """

   dev_data = {}
   a_yaml_file = open("db.txt")    # read the databse (actually a single YAML file)
   db = yaml.load(a_yaml_file, Loader=yaml.FullLoader)

   # extract info from the db and create the dev centered object
   try:
       dev_data['site']     = find_attribut ('sites',       site_name, db)
       dev_data['tenant']   = find_attribut ('tenants',     dev_data['site']['tenant'],    db)
       dev_data['topology'] = find_attribut ('topologies',  dev_data['site']['topology'],  db)
       dev_data['contrat']  = find_attribut ('contrats',    dev_data['site']['contrat'],   db)
       # get the role inside the found topology
       dev_data['role']     = find_attribut ('roles',       role_name, dev_data['topology'])

       # templates: merge tenant, topology and role templates
       dev_data['templates']  = []
       for hierarchy in [ 'tenant', 'topology', 'role' ]:
           if 'templates' in dev_data[hierarchy]:
              # retrieve template data in templates hierarchy
              for tmpl in dev_data[hierarchy]['templates']:
                 tmpl_data = find_attribut ('templates', tmpl['name'], db)
                 print ("add templates : ", tmpl_data )
                 dev_data['templates'].append ( tmpl_data )
   except:
       print("Error: ", sys.exc_info()[0])
       raise

   return dev_data

if __name__=="__main__":
   if len(sys.argv)!=3: 
      print ( "Usage: {} Site Role".format(sys.argv[0]) )
      print ( "\nExample: {} Limoges001 dual2\n".format(sys.argv[0]) )
   else:
      info = get_dev_data (sys.argv[1], sys.argv[2])
      for sub in info:
         print (sub, "is \n", info[sub], "\n------------------\n")

