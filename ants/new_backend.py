from subprocess import call, Popen, PIPE
import re
import sys
from ipaddress import *
from pyroute2 import IPDB
from iptc import Table, Rule, Target

class NetworkCell:
	def __init__(self):
		self.essid = ""
		self.frequency = ""
	def __str__(self):
		return self.essid + ", " + self.frequency

class NetworkHost:
	def __init__(self):
		self.name = ""
		self.mac = ""
		self.ip_real = ""
		self.ip_virtual = ""
		self.type = ""
		self.id = ""

	def __str__(self):
		str = "logical name: " + self.name + "\n"
		str += "mac address: " + self.mac + "\n"
		str += "physical id: " + self.id + "\n"
		str += "type: " + self.type + "\n"
		str += "real ip address: " + self.ip_real + "\n"
		str += "virtual ip address: " + self.ip_virtual + "\n"

		return str


	def assign_ip(self):
		with IPDB() as ipdb:
			with ipdb.interfaces[self.name] as i:
				i.add_ip(self.ip_real+'/24')
				i.up()
			ipdb.release()

	def disconnect_network(self):
		if self.type == "Wireless":
			call(['iwconfig', self.name, 'essid', 'off'])
		else:
			print("THIS IS NOT A WIRELESS INTERFACE")



	def scan_network(self, frequency):
		if self.type == "Wireless":
			with IPDB() as ipdb:
				with ipdb.interfaces[self.name] as i:
					i.up()
				ipdb.release()
			p = Popen(['iwlist', self.name, 'scan'], stdout=PIPE, stderr=PIPE)
			data, error = p.communicate()
			data = str(data)
			cells = get_frequency_cells(data, frequency)
			return cells
		else:
			print("THIS IS NOT A WIRELESS INTERFACE")

	def	network_status(self, essid):
		if self.type == "Wireless":
			p = Popen(['iwconfig', self.name],stdout=PIPE, stderr=PIPE)
			data = str(p.communicate()[0])
			if "Not-Associated" in data:
				return False
			elif essid in data:
				return True
		else:
			print("THIS IS NOT A WIRELESS INTERFACE")
			return False


	def connect_network(self, essid):
		if self.type == "Wireless":
			call(['iwconfig', self.name, 'essid', essid])
			for i in range(0,15):
				if self.network_status(essid):
					return True
		else:
			print("THIS IS NOT A WIRELESS INTERFACE")
		return False

	def ping(self, destination_ip):
		ping_max = 60
		ping_args = "ping -c 1 -I {0} {1}".format(self.name, destination_ip).split(" ")
		ping_count = 1
		print("WAITING FOR PING SUCCESS:")
		while ping_count <= ping_max:
			print(".", end = '')
			sys.stdout.flush()
			ping_process = Popen(ping_args, stdout=PIPE, stderr=PIPE)
			ping_process.communicate()[0]
			rc = ping_process.returncode
			if int(rc) == 0:
				print("\nPING SUCCEEDED AFTER {0} RUN(S)".format(ping_count))
				return True
			ping_count = ping_count + 1
		print("\nPING FAILED AFTER {0} ATTEMPTS".format(ping_max))
		return False

def ip_calculations(ap_ip_address, client_host, server_host):
	# real
	client_host.ip_real = str(ip_address(ap_ip_address) + 1)
	print("CLIENT IP ADDRESS is: ", client_host.ip_real)
	server_host.ip_real = str(ip_address(ap_ip_address) + 2)
	print("SERVER IP ADDRESS is: ", server_host.ip_real)
	# virtual
	client_host.ip_virtual = str(ip_address(client_host.ip_real) + (256))
	print("VIRTUAL CLIENT IP ADDRESS is: ", client_host.ip_virtual)
	server_host.ip_virtual = str(ip_address(server_host.ip_real) + (256))
	print("VIRTUAL SERVER IP ADDRESS is: ", server_host.ip_virtual)

def __get_type(s):
	m = re.search("description: (\w+)", s)
	if m:
		return m.group(1)
	return None

def __get_serial(s):
	m = re.search("serial: (([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2}))", s)
	if m:
		return m.group(1)
	return None

def __get_id(s):
	m = re.search("physical id: ([0-9]+([.][0-9])*)", s)
	if m:
		return m.group(1)
	return None

def __get_name(s):
	m = re.search("logical name: (\w+)", s)
	if m:
		return m.group(1)
	return None

def get_devices():
	print("SCANNING HW NETWORK INTERFACES")
	p = Popen(['lshw','-class','network'], stdout=PIPE, stderr=PIPE)
	data, error = p.communicate()
	arr = str(data).split("*-network")

	dev_eth_list = []
	dev_wlan_list = []

	for a in arr:
		t = __get_type(a)
		if t:
			if "Ethernet" in t:
				dev_eth = NetworkHost()
				dev_eth.name = __get_name(a)
				dev_eth.mac = __get_serial(a)
				dev_eth.type = "Ethernet"
				dev_eth.id =  __get_id(a)
				dev_eth_list.append(dev_eth)
			elif "Wireless" in t:
				dev_wlan = NetworkHost()
				dev_wlan.name = __get_name(a)
				dev_wlan.mac = __get_serial(a)
				dev_wlan.type = "Wireless"
				dev_wlan.id =  __get_id(a)
				dev_wlan_list.append(dev_wlan)
	return dev_eth_list, dev_wlan_list

def get_frequency(s):
	m = re.search("Frequency:([0-9][.][0-9]*) GHz", s)
	if m:
		return m.group(1)
	return None

def get_essid(s):
	m = re.search("ESSID:\"(.*)\"", s)
	if m:
		return m.group(1)
	return None

def get_frequency_cells(s, fc):
	cells = []
	arr = s.split("Cell")
	index = 0
	for a in arr:
		if index != 0:
			c = NetworkCell()
			c.essid = get_essid(a)
			c.frequency = get_frequency(a)
			if float(c.frequency) == float(fc):
				cells.append(c)
		index = index + 1
	return cells


def setup_routing(client_host, server_host):

	iptables_list = "iptables -t nat -L".split(" ")
	iptables_flush = "iptables -t nat -F".split(" ")

	iptables_two_args = "iptables -t nat -A POSTROUTING -s " + server_host.ip_real + " -d " + client_host.ip_virtual + " -j SNAT --to-source " + server_host.ip_virtual
	iptables_three_args = "iptables -t nat -A PREROUTING -d " + server_host.ip_virtual + " -j DNAT --to-destination " + server_host.ip_real
	ip_route_two_args = "ip route add " + server_host.ip_virtual + " dev " + client_host.name
	arp_two_args = "arp -i " + client_host.name + " -s " + server_host.ip_virtual + " " + server_host.mac

	iptables_four_args = "iptables -t nat -A POSTROUTING -s " + client_host.ip_real + " -d " + server_host.ip_virtual + " -j SNAT --to-source " + client_host.ip_virtual
	iptables_five_args = "iptables -t nat -A PREROUTING -d " + client_host.ip_virtual + " -j DNAT --to-destination " + client_host.ip_real
	ip_route_one_args = "ip route add " + client_host.ip_virtual + " dev " + server_host.name
	arp_one_args = "arp -i " + server_host.name + " -s " + client_host.ip_virtual + " " + client_host.mac

	flush_route = "ip route flush table main".split(" ")
	show_route = "ip route show table main".split(" ")

	call(iptables_flush)
	call(iptables_two_args.split(" "))
	call(iptables_three_args.split(" "))
	call(iptables_four_args.split(" "))
	call(iptables_five_args.split(" "))
	call(ip_route_one_args.split(" "))
	call(arp_one_args.split(" "))
	call(ip_route_two_args.split(" "))
	call(arp_two_args.split(" "))
	call(iptables_list)
	call(show_route)

def setup_routing2(client_host, server_host):

    table = Table(Table.NAT)
    table.flush()

    chain_pre = [ch for ch in table.chains if 'PREROUTING' in ch.name][0]
    chain_post = [ch for ch in table.chains if 'POSTROUTING' in ch.name][0]

    snat_r1 = Rule()
    snat_r1.src = server_host.ip_real
    snat_r1.dst = client_host.ip_virtual
    snat_r1.target = snat_r1.create_target("SNAT")
    snat_r1.target.to_source = server_host.ip_virtual
    chain_post.append_rule(snat_r1)

    snat_r2 = Rule()
    snat_r2.src = client_host.ip_real
    snat_r2.dst = server_host.ip_virtual
    snat_r2.target = snat_r2.create_target("SNAT")
    snat_r2.target.to_source = client_host.ip_virtual
    chain_post.append_rule(snat_r2)

    dnat_r1 = Rule()
    dnat_r1.dst = server_host.ip_virtual
    dnat_r1.target = dnat_r1.create_target("DNAT")
    dnat_r1.target.to_destination = server_host.ip_real
    chain_pre.append_rule(dnat_r1)

    dnat_r2 = Rule()
    dnat_r2.dst = client_host.ip_virtual
    dnat_r2.target = dnat_r2.create_target("DNAT")
    dnat_r2.target.to_destination = client_host.ip_real
    chain_pre.append_rule(dnat_r2)

    ip_route_one_args = "ip route add " + client_host.ip_virtual + " dev " + server_host.name
    ip_route_two_args = "ip route add " + server_host.ip_virtual + " dev " + client_host.name
    arp_one_args = "arp -i " + server_host.name + " -s " + client_host.ip_virtual + " " + client_host.mac
    arp_two_args = "arp -i " + client_host.name + " -s " + server_host.ip_virtual + " " + server_host.mac
    show_route = "ip route show table main".split(" ")
    iptables_list = "iptables -t nat -L".split(" ")

    call(ip_route_one_args.split(" "))
    call(arp_one_args.split(" "))
    call(ip_route_two_args.split(" "))
    call(arp_two_args.split(" "))

    call(iptables_list)
    call(show_route)
