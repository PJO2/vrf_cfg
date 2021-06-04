# ---------------------------------------
# netconf API 
# ---------------------------------------

from ncclient import manager
import xmltodict
import json
import re

#
# Namespaces starting point for xpath queries
#
ns_dict = {
    'nc': 'urn:ietf:params:xml:ns:netconf:base:1.0'
}

ns_getcontract_filter = '''
     <nc:filter  type="xpath"
                 xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"
                 xmlns:rm="http://cisco.com/ns/yang/Cisco-IOS-XE-route-map"
                 select="/native/route-map[rm:route-map-without-order-seq/seq_no='{}']/name"
               />
'''

ns_getsites_filter = '''
     <nc:filter  type="xpath"
                 xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"
                 xmlns:rm="http://cisco.com/ns/yang/Cisco-IOS-XE-route-map"
                 select="/native/route-map[substring(name, 1, 3)='To_']/name"
               />
'''
ns_getroutes_filter = '''
        <nc:filter  type="xpath"
                 xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"
                 xmlns:na="http://cisco.com/ns/yang/Cisco-IOS-XE-native"
                 xmlns:rb="http://cisco.com/ns/yang/Cisco-IOS-XE-bgp"
                 xmlns:bo="http://cisco.com/ns/yang/Cisco-IOS-XE-bgp-oper"
                 select="/bo:bgp-state-data/bgp-route-rds[contains (bgp-route-rd/rd-value, ':')]/bgp-route-rd/bgp-rd-route-afs/bgp-rd-route-af[afi-safi='vpnv4-unicast']/bgp-rd-route-filters/bgp-rd-route-filter/bgp-rd-route-entries/bgp-rd-route-entry[contains (bgp-rd-path-entries/bgp-rd-path-entry/extended-community, 'RT:65500:555')]/prefix"
               />
'''

def build_sites_list():
    m = manager.connect( host='10.112.83.100',
                       port=830,
                       username='cisco',
                       password='cisco',
                       hostkey_verify=False)
    answer = m.get_config(source='running', filter=ns_getsites_filter).data_xml
    c = xmltodict.parse (answer)
    # build the list
    liste_sites = [ r['name'][3:]   for r in c['data']['native']['route-map'] ]
    return json.dumps (liste_sites, indent=4)


def build_contract_info(contract_id):
    """  get all sites assigned to a contract

    given a contract's id, the function retrieve all sites linked to it
    parse the route-map configuration to retrieve the route-map which contain
    match extcommunity {{ contrcat_id }}
    like :
         route-map To_zutabimntl permit 543
           description -- site is zutabimntl }}, contract is contract --
           match extcommunity 543
    netconf api returns a XML list of records with the following structure :
         <route-map>
             <name>To_zutabimntl</name>
             <route-map-without-order-seq xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-route-map">
               <seq_no>543</seq_no>
               <match>
                  <extcommunity>
                      <name>543</name>
                  </extcommunity>
                </match>
             </route-map-without-order-seq>
         </route-map>
    the actual filter does only return the name in XML formtat:
      <route-map>
        <name>To_xcuopwfgen</name>
      </route-map>
    """
    m = manager.connect( host='10.112.83.100',
                       port=830,
                       username='cisco',
                       password='cisco',
                       hostkey_verify=False)
    # resolve contract id
    xpath_filter = ns_getcontract_filter.format(contract_id)
    answer = m.get_config(source='running', filter=xpath_filter).data_xml 
    c = xmltodict.parse (answer)
    # build the list
    liste_sites = [ r['name'][3:]   for r in c['data']['native']['route-map'] ]
    return json.dumps (liste_sites, indent=4)


def build_contract_route(contract_id):
    """ retrieve the routes belonging to a contract

    explore the bgp route table and extract the routes having
    a extcommunity linke RT:65500:{{contrcat_id}}
    """
    m = manager.connect( host='10.112.83.100',
                       port=830,
                       username='cisco',
                       password='cisco',
                       hostkey_verify=False)
    # resolve contract id
    xpath_filter = ns_getroutes_filter.format(contract_id)
    answer = m.get (filter=xpath_filter).data_xml
    c = xmltodict.parse (answer)
    # build the list
    list_routes = [ prefix['prefix'] for prefix in c['data']['bgp-state-data']['bgp-route-rds']['bgp-route-rd']['bgp-rd-route-afs']['bgp-rd-route-af']['bgp-rd-route-filters']['bgp-rd-route-filter']['bgp-rd-route-entries']['bgp-rd-route-entry'] ]
    return json.dumps (list_routes, indent=4)



# An api example
# -----------------
import sys
# get all configuration for the contract id given as a parameter
if __name__ == "__main__":
    print ( build_routes_info("Contract_555") )
    quit()
    print ( build_sites_list() )
    input ("type  enter for contract test")
    print ( build_contract_info ("534") )
 
