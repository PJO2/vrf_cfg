#!/ usr/bin/python3
# --------------------------------
# REST API requests to the router
# migrated to netconf for more precise xpath processing
# -------------------------------


import requests
import json


import config


URLs =   { 'contracts': '/restconf/data/native/ip/extcommunity-list/standard' ,
           'sites':     '/restconf/data/native/route-map?fields=name' ,
           'site':      '/restconf/data/native/route-map=To_{}/route-map-without-order-seq' ,
         }

headers = { 'Content-Type': 'application/json', 'Accept': 'application/yang-data+json' }



def build_contracts_list():
   """ return the contracts names

   list all extended community-list and map them to contract name + id
   """
   url = 'https://' + config.HUBs[0] + URLs['contracts']
   print(url)
   answer = requests.get (url, auth = requests.auth.HTTPBasicAuth( 'cisco', 'cisco'), headers=headers, verify = False).json()
#   if answer.status_code in [200,202,204]:
   if True:
      ctc = []
      for comm in answer["Cisco-IOS-XE-bgp:standard"]:
          ctc.append(  { 'name': comm['name'], 'id': comm['permit']['rt'][0]['name'][len("65500:"):] }  )
      return ctc
   else:
      print ("Error in API request")
      return None

  
def build_sites_list():
   url = 'https://' + config.HUBs[0] + URLs['sites']
   print(url)
   answer = requests.get (url, auth = requests.auth.HTTPBasicAuth( 'cisco', 'cisco'), headers=headers, verify = False).json()
   sites = [ ctc['name'][3:]    for ctc in answer["Cisco-IOS-XE-native:route-map"] if ctc['name'].startswith('To_') ]
   return sites

  
def build_site_info(site_name):
   url = 'https://' + config.HUBs[0] + URLs['site'].format(site_name)
   print(url)
   answer = requests.get (url, auth = requests.auth.HTTPBasicAuth( 'cisco', 'cisco'), headers=headers, verify = False).json()
   return  answer["Cisco-IOS-XE-route-map:route-map-without-order-seq"]

# --------------------------------
if __name__ == "__main__":
   print (build_contracts_list())

