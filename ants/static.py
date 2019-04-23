import time
from new_backend import *
from subprocess import call


eth_list, wlan_list = get_devices()
for eth in eth_list:
    print(eth)
for wlan in wlan_list:
    print(wlan)

ap_ip_address = "10.1.1.10"
ip_calculations(ap_ip_address, eth, wlan)

eth.assign_ip()
eth.ping("10.1.1.10")

wlan.disconnect_network()
network_list = wlan.scan_network('5.765')
for network in network_list:
    print(network)
essid = "Belair-5G"
wlan.connect_network(essid)
wlan.assign_ip()
wlan.ping("10.1.1.10")

setup_routing2(eth,wlan)

wlan.ping(eth.ip_virtual)
eth.ping(wlan.ip_virtual)
