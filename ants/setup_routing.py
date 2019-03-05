import subprocess
import netifaces

def setup_routing(client_device_name, client_mac_address, server_device_name, server_mac_address, client_ip_address, virtual_client_ip_address, server_ip_address, virtual_server_ip_address):

	server_ip_args = "ip addr add {0}/24 dev {1}".format(server_ip_address, server_device_name).split(" ")
	client_ip_args = "ip addr add {0}/24 dev {1}".format(client_ip_address, client_device_name).split(" ")

	iptables_one_args = "iptables -t nat -L".split(" ")
	iptables_flush = "iptables -t nat -F".split(" ")

	iptables_two_args = "iptables -t nat -A POSTROUTING -s " + server_ip_address + " -d " + virtual_client_ip_address + " -j SNAT --to-source " + virtual_server_ip_address
	iptables_three_args = "iptables -t nat -A PREROUTING -d " + virtual_server_ip_address + " -j DNAT --to-destination " + server_ip_address
	iptables_four_args = "iptables -t nat -A POSTROUTING -s " + client_ip_address + " -d " + virtual_server_ip_address + " -j SNAT --to-source " + virtual_client_ip_address
	iptables_five_args = "iptables -t nat -A PREROUTING -d " + virtual_client_ip_address + " -j DNAT --to-destination " + client_ip_address

	ip_route_one_args = "ip route add " + virtual_client_ip_address + " dev " + server_device_name
	arp_one_args = "arp -i " + server_device_name + " -s " + virtual_client_ip_address + " " + client_mac_address

	ip_route_two_args = "ip route add " + virtual_server_ip_address + " dev " + client_device_name
	arp_two_args = "arp -i " + client_device_name + " -s " + virtual_server_ip_address + " " + server_mac_address
	flush_route = "ip route flush table main".split(" ")
	show_route = "ip route show table main".split(" ")
	subprocess.call(show_route)
	subprocess.call(flush_route)
	subprocess.call(iptables_flush)
	subprocess.call(server_ip_args)
	subprocess.call(client_ip_args)
	subprocess.call(iptables_two_args.split(" "))
	subprocess.call(iptables_three_args.split(" "))
	subprocess.call(iptables_four_args.split(" "))
	subprocess.call(iptables_five_args.split(" "))
	subprocess.call(ip_route_one_args.split(" "))
	subprocess.call(arp_one_args.split(" "))
	subprocess.call(ip_route_two_args.split(" "))
	subprocess.call(arp_two_args.split(" "))
	subprocess.call(iptables_one_args)
	subprocess.call(show_route)
