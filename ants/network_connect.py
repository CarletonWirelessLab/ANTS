from subprocess import *

def is_associated(wlan_name, essid):
	p = Popen(['iwconfig',wlan_name],stdout=PIPE, stderr=PIPE)
	data = str(p.communicate()[0])
	if essid in data:
		print(wlan_name, "ASSOCIATED TO ESSID:" , essid)#)
		return 1
	return 0

def network_connect(wlan_name, server_ip_address, essid, wlan_internal_name):
	show_route = "ip route show table main".split(" ")
	flush_route = "ip route flush table main".split(" ")
	print("BRINGING",wlan_internal_name,"DOWN")
	call(['ifconfig', wlan_internal_name, 'down'])
	print("FLUSHING IP ROUTE TABLE")
	call(flush_route)

	print("BRINGING",wlan_name,"DOWN")
	call(['ifconfig', wlan_name, 'down'])

	print("BRINGING",wlan_name,"UP")
	call(['ifconfig', wlan_name, 'up'])
	call(['ip', 'addr', 'flush', 'dev', wlan_name])


	print("ASSOCIATING", wlan_name, "TO ESSID", essid)
	call(['iwconfig', wlan_name, 'essid', essid])
	print("WAITING FOR" , wlan_name, "TO ASSOCIATE TO ESSID", essid)
	while not is_associated(wlan_name, essid):
		pass
	print("ASSIGNING",wlan_name,"TO IP:",server_ip_address)
	call(['ifconfig', wlan_name, 'inet', server_ip_address])
	print("SHOWING ROUTE TABLE")
	call(show_route)
