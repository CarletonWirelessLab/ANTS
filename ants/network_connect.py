from subprocess import Popen, PIPE

def network_connect(eth_name, client_ip_address, wlan_name, server_ip_address, essid):
	Popen(['ifconfig', eth_name, 'inet', client_ip_address], stdout=PIPE, stderr=PIPE).communicate()
	Popen(['iwconfig', wlan_name, 'essid', essid], stdout=PIPE, stderr=PIPE).communicate()
	Popen(['ifconfig', wlan_name, 'inet', server_ip_address], stdout=PIPE, stderr=PIPE).communicate()    

