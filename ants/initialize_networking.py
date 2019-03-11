
from interfaces_scan import *
from network_scan import *
from network_connect import *
from ipaddress import *
from setup_routing import *
from re import *
from subprocess import *
import time
def initialize_networking(ap_ip_address):
	# real
	client_ip_address = str(ip_address(ap_ip_address) + 1)
	print("CLIENT IP ADDRESS is: " , client_ip_address)
	server_ip_address = str(ip_address(ap_ip_address) + 2)
	print("SERVER IP ADDRESS is: " , server_ip_address)
	# virtual
	virtual_client_ip_address = str(ip_address(client_ip_address) + (256))
	print("VIRTUAL CLIENT IP ADDRESS is: " , virtual_client_ip_address)
	virtual_server_ip_address = str(ip_address(server_ip_address) + (256))
	print("VIRTUAL SERVER IP ADDRESS is: " , virtual_server_ip_address)


	eth_name, eth_mac, wlan_name, wlan_mac, wlan_internal_name = interfaces_scan()
	print("BRINGING",wlan_name,"DOWN")
	call(['ifconfig', wlan_name, 'down'])
	call(['ip', 'addr', 'flush', 'dev', wlan_name])

	print("BRINGING",eth_name,"UP")
	call(['ifconfig', eth_name, 'up'])
	call(['ip', 'addr', 'flush', 'dev', eth_name])

	print("ASSIGNING",eth_name,"TO IP:",client_ip_address)
	call(['ifconfig', eth_name, 'inet', client_ip_address, 'up'])
	ping_args = "ping -c 10 -I {0} {1}".format(eth_name, ap_ip_address).split(" ")
	ping_count = 0
	print("WAITING FOR PING SUCCESS OF THE ACCESS POINT THROUGH THE CLIENT INTERFACE")
	communication_success = 0
	ping_max = 10
	while ping_count < ping_max:
		ping_process = Popen(ping_args, stdout=PIPE, stderr=PIPE)
		ping_process.communicate()[0]
		rc = ping_process.returncode
		if int(rc) == 0:
			print("PING SUCCEEDED AFTER {0} RUNS".format(ping_count+1))
			communication_success = 1
			break
		ping_count = ping_count + 1
	if ping_count == ping_max:
		print("PING FAILED AFTER {0} ATTEMPTS".format(ping_max))
		communication_success = 0

	tcpdump_args = "tcpdump -c 1 -i " + eth_name
	p = Popen(tcpdump_args.split(" "), stdout=PIPE, stderr=PIPE)
	data, error = p.communicate()
	rc = p.returncode
	data = str(data)
	bridge_id = data


	print("BRINGING",wlan_name,"UP")
	call(['ifconfig', wlan_name, 'up'])
	essid = network_scan(wlan_name,bridge_id)
	network_connect(wlan_name, server_ip_address, essid, wlan_internal_name)

	setup_routing(eth_name, eth_mac, wlan_name, wlan_mac, client_ip_address, virtual_client_ip_address, server_ip_address, virtual_server_ip_address)

	return eth_name, client_ip_address, server_ip_address, virtual_server_ip_address
