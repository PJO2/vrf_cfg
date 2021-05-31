from ncclient import manager
import re

#
# Namespaces starting point for xpath queries
#
ns_dict = {
    'nc': 'urn:ietf:params:xml:ns:netconf:base:1.0'
}

def cook_xpath(xpath):
    # The basic XPath filter, in XML, looks like:
    #
    # <nc:filter type="xpath"
    #            xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"
    #            xmlns:if="urn:ietf:params:xml:ns:yang:ietf-interfaces"
    #            select="/some/x/path/query"/>)
    #
    # We need to:
    # - identify all "ns:" occurrences
    # - create a namespace mapping that we will put in the XML outside select
    # - construct the XML
    #
    filter_template = '<nc:filter type="xpath" %s select="%s"/>'
    ns_set = {'nc'}
    re_ns = re.compile('([\w\-]+):([\w\-]+)')
    for prefix, local_name in re_ns.findall(xpath):
        if prefix not in ns_dict:
            print('Required prefix "%s" not defined' % prefix)
            sys.exit(1)
        else:
            ns_set.add(prefix)
    namespaces = ' '.join(['xmlns:%s="%s"' % (p, ns_dict[p]) for p in ns_set])
    xml_xpath = filter_template % (namespaces, xpath)
    print(xml_xpath)
    return xml_xpath



def build_sites_list2():
    m = manager.connect( host='10.112.83.100',
                       port=830,
                       username='cisco',
                       password='cisco',
                       hostkey_verify=False)
    c = m.get_config(source='running', filter=cook_xpath("/native/route-map[substring(name, 1, 3)='To']")).data_xml
    return c


def build_contract_info(contract_id):
    m = manager.connect( host='10.112.83.100',
                       port=830,
                       username='cisco',
                       password='cisco',
                       hostkey_verify=False)
    xpath = "/native/route-map//match/extcommunity[name='{}']".format(contract_id)
    c = m.get_config(source='running', filter=cook_xpath(xpath)).data_xml


