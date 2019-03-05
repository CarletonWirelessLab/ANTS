
from interfaces_scan import *
from network_scan import *
from network_connect import *
from ipaddress import *
from setup_routing import *
from re import *

def initialize_networking(ap_ip_address):
	ap_ip_address_octets = ap_ip_address.split('.')
	if int(ap_ip_address_octets[0]) == 192 and int(ap_ip_address_octets[1]) == 168:
		# real
		client_ip_address = str(ip_address(ap_ip_address) + 1)
		print("CLIENT IP ADDRESS is: " , client_ip_address)
		server_ip_address = str(ip_address(ap_ip_address) + 2)
		print("SERVER IP ADDRESS is: " , server_ip_address)
		virtual_client_ip_address = str(ip_address(client_ip_address) + (256))
		print("VIRTUAL CLIENT IP ADDRESS is: " , virtual_client_ip_address)
		virtual_server_ip_address = str(ip_address(server_ip_address) + (256))
		print("VIRTUAL SERVER IP ADDRESS is: " , virtual_server_ip_address)
	else:
		# real
		client_ip_address = str(ip_address(ap_ip_address) + 1)
		print("CLIENT IP ADDRESS is: " , client_ip_address)
		server_ip_address = str(ip_address(ap_ip_address) + 2)
		print("SERVER IP ADDRESS is: " , server_ip_address)
		virtual_client_ip_address = str(ip_address(client_ip_address) + (256*256))
		print("VIRTUAL CLIENT IP ADDRESS is: " , virtual_client_ip_address)
		virtual_server_ip_address = str(ip_address(server_ip_address) + (256*256))
		print("VIRTUAL SERVER IP ADDRESS is: " , virtual_server_ip_address)

	eth_name, eth_mac, wlan_name, wlan_mac, wlan_internal_name = interfaces_scan()

	route_show_args = "ip route show"
	p = Popen(route_show_args.split(" "), stdout=PIPE, stderr=PIPE)
	data, error = p.communicate()
	data = str(data)

	essid = network_scan(wlan_name)
	network_connect(eth_name, client_ip_address, wlan_name, server_ip_address, essid, wlan_internal_name)
	setup_routing(eth_name, eth_mac, wlan_name, wlan_mac, client_ip_address, virtual_client_ip_address, server_ip_address, virtual_server_ip_address)

	return eth_name, client_ip_address, server_ip_address, virtual_server_ip_address
