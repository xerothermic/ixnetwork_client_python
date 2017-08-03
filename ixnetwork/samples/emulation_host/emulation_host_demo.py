import sys
import os
path = os.path.realpath(__file__)
sys.path.insert(0, path[0: path.rfind('ixnetwork')])

from ixnetwork.IxnHttp import IxnHttp
from ixnetwork.IxnConfigManagement import IxnConfigManagement
from ixnetwork.IxnPortManagement import IxnPortManagement
from ixnetwork.IxnStatManagement import IxnStatManagement
from ixnetwork.IxnEmulationHosts import IxnIgmpHostEmulation, IxnIpv4Emulation
import os
import time
import json


# connect to an existing session
ixnhttp = IxnHttp('10.200.22.48', rest_port=12345)
ixnhttp.trace = True
ixnhttp.current_session = ixnhttp.sessions()[0]


# print system information
print(ixnhttp.system_info)


# load a json configuration
config_mgmt = IxnConfigManagement(ixnhttp)
config_filename = '%s/emulation-host-demo.json' % os.path.dirname(os.path.realpath(__file__))
with open(config_filename, 'r') as fid:
    json_config = json.loads(fid.read())


# change the virtual port type to ethernet in the json config
for vport in json_config['vport']:
    vport['l1Config']['currentType'] = 'ethernet'


# import the updated configuration
config_mgmt.import_config(json_config)


# assign hardware ports to virtual ports
# port_mgmt = IxnPortManagement(ixnhttp)
# port_mgmt.map('PE2-6/5', '10.200.109.3', '1', '1') \
#     .map('PE2-6/8', '10.200.109.3', '1', '2') \
#     .apply()


# find igmp emulation host session(s) by vport_name and mac addresses
igmp = IxnIgmpHostEmulation(ixnhttp)
igmp.find(vport_name='PE2-6/5', versionType='version2')
print(igmp.session_ids)


# find ipv4 emulation host session(s) by vport_name 
ipv4 = IxnIpv4Emulation(ixnhttp)
ipv4.find(vport_name='PE2-6/8')
print(ipv4.session_ids)


# low level API start all protocols
ixnhttp.root.operations.startallprotocols()


# wait for ipv4 and igmp emulation sessions to be in an up state
ipv4.wait_until(IxnIpv4Emulation.STATE_UP, timeout=90)
igmp.wait_until(IxnIgmpHostEmulation.STATE_UP, timeout=90)


# stop the ipv4 and igmp emulation sessions
igmp.stop(IxnIgmpHostEmulation.STATE_NOTSTARTED, timeout=90)
ipv4.stop(IxnIpv4Emulation.STATE_NOTSTARTED, timeout=90)


# print statistics
time.sleep(5)
stat_mgmt = IxnStatManagement(ixnhttp)
views = stat_mgmt.get_views()
print(views)
port_summary_page = stat_mgmt.get_view_page('Port Summary')
stat_mgmt.print_view_page(port_summary_page, column_captions=[
    'Port', 'Sessions Total', 'Sessions Up', 'Sessions Down', 'Sessions Not Started'])
protocols_summary_page = stat_mgmt.get_view_page('Protocols Summary')
stat_mgmt.print_view_page(protocols_summary_page, column_captions=[
    'Protocol Type', 'Sessions Total', 'Sessions Up', 'Sessions Down', 'Sessions Not Started'])

