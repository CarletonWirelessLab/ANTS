import subprocess

def network_connect(eth_name, client_ip_address, wlan_name, server_ip_address, essid):
	subprocess.call(['ifconfig', eth_name, 'inet', client_ip_address])
	subprocess.call(['iwconfig', wlan_name, 'essid', essid])
	subprocess.call(['ifconfig', wlan_name, 'inet', server_ip_address])    

