from subprocess import *

def is_associated(wlan_name, essid):
	p = Popen(['iwconfig',wlan_name],stdout=PIPE, stderr=PIPE)
	data = str(p.communicate()[0])
	if essid in data:
		print(wlan_name, "ASSOCIATED TO:" , essid)
		return 1
	return 0






def network_connect(eth_name, client_ip_address, wlan_name, server_ip_address, essid, wlan_internal_name):
	print("BRINGING",wlan_internal_name,"DOWN")
	call(['ifconfig', wlan_internal_name, 'down'])
	show_route = "ip route show table main".split(" ")
	print("SHOWING ROUTE TABLE IN NETWORK CONNECT 111111########")
	call(show_route)
	flush_route = "ip route flush table main".split(" ")
	print("FLUSHING TABLE   ########")
	call(flush_route)
	call(['ifconfig', eth_name, 'down'])
	call(['ifconfig', wlan_name, 'down'])
	call(['ifconfig', eth_name, 'up'])
	call(['ifconfig', wlan_name, 'up'])
	call(['ip', 'addr', 'flush', 'dev', wlan_name])
	call(['ip', 'addr', 'flush', 'dev', eth_name])
	print("SHOWING ROUTE TABLE IN NETWORK CONNECT   222222########")
	call(show_route)
	call(['ifconfig', eth_name, 'inet', client_ip_address])
	# ping_args = "ping -w 1 {0}".format(self.iperf_virtual_server_addr).split(" ")
	# ping_count = 0
	# print("WAITING FOR VIRTUAL CONNECTION TO BE CONFIGURED\n")
	# while ping_count < self.ping_max:
	# 	ping_process = subprocess.Popen(ping_args)
	# 	ping_process.communicate()[0]
	# 	rc = ping_process.returncode
	# 	if int(rc) == 0:
	# 		print("PING SUCCEEDED AFTER {0} RUNS\n".format(ping_count))
	# 		break
	# 	ping_count = ping_count + 1
	# if ping_count == self.ping_max:
	# 	print("FAILED TO COMMUNICATE WITH ACCESS POINT AFTER {0} ATTEMPTS\n".format(self.ping_max))




	call(['iwconfig', wlan_name, 'essid', essid])
	print("WAITING FOR" , wlan_name, "TO ASSOCIATE TO", essid)
	while not is_associated(wlan_name, essid):
		pass
	call(['sleep', '10'])
	call(['ifconfig', wlan_name, 'inet', server_ip_address])
	print("SHOWING ROUTE TABLE IN NETWORK CONNECT   333333########")
	call(show_route)
