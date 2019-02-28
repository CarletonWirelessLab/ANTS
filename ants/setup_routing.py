import subprocess
import netifaces

def setup_routing():
	ip_address_list = []
	mac_address_list = []
	device_name_list = []

	for device_name in netifaces.interfaces():
		link = netifaces.ifaddresses(device_name)
		try:
			if device_name != 'lo':
				ip_address = link[2][0]['addr']
				mac_address = link[17][0]['addr']
				ip_address_list.append(ip_address)
				mac_address_list.append(mac_address)
				device_name_list.append(device_name)
				print("FOUND DEVICE " + device_name + " WITH IP ADDRESS " + ip_address + " WITH MAC ADDRESS " + mac_address)
		except:
			print("THIS DEVICE " + device_name + " HAS NO IP ADDRESS")

	index = 0
	for device_name in device_name_list:
		print (device_name)
		if device_name[0] == 'e':
			client_device_name = device_name
			client_ip_address = ip_address_list[index]
			client_mac_address = mac_address_list[index]
			print("Client device MAC address is {0}\n".format(client_mac_address))
		else:
			server_device_name = device_name
			server_ip_address = ip_address_list[index]
			server_mac_address = mac_address_list[index]
			print("Server device MAC address is {0}\n".format(server_mac_address))
		index += 1
	
		
	index_first_dot = client_ip_address.index('.')
	if client_ip_address[index_first_dot+1] != '2':    
		virtual_client_ip_address = client_ip_address[0:index_first_dot+1] + str(int(client_ip_address[index_first_dot+1])+1) + client_ip_address[index_first_dot+2:]
	else:
		virtual_client_ip_address = client_ip_address[0:index_first_dot+1] + str(int(client_ip_address[index_first_dot+1])-1) + client_ip_address[index_first_dot+2:]


	index_first_dot = server_ip_address.index('.')
	if server_ip_address[index_first_dot+1] != '2':    
		virtual_server_ip_address = server_ip_address[0:index_first_dot+1] + str(int(server_ip_address[index_first_dot+1])+1) + server_ip_address[index_first_dot+2:]
	else:
		virtual_server_ip_address = server_ip_address[0:index_first_dot+1] + str(int(server_ip_address[index_first_dot+1])-1) + server_ip_address[index_first_dot+2:]

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

	print("Network routing should now be ready for use with ANTS.\n")

	return client_ip_address, server_ip_address , virtual_server_ip_address
