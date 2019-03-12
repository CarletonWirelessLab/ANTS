import re
from subprocess import Popen, PIPE

class Dev:
	def __init__(self, t, a, i, n):
		self.type = t
		self.mac_addr = a
		self.id = i
		self.name = n
	def __str__(self):
		return self.type + ", " + self.name + ", " + self.mac_addr + ", " + self.id

def get_type(s):
	m = re.search("description: (\w+)", s)
	if m:
		return m.group(1)
	return None

def get_serial(s):
	m = re.search("serial: (([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2}))", s)
	if m:
		return m.group(1)
	return None

def get_id(s):
	m = re.search("physical id: ([0-9]+([.][0-9])*)", s)
	if m:
		return m.group(1)
	return None

def get_name(s):
	m = re.search("logical name: (\w+)", s)
	if m:
		return m.group(1)
	return None

# returns the last two devices 1 ether and 1 wireless
def get_devices(s):
	arr = s.split("*-network")
	for a in arr:
		t = get_type(a)
		if t:
			if "Ethernet" in t:
				dev_eth = Dev("eth", get_serial(a), get_id(a), get_name(a))
			elif "Wireless" in t and get_id(a) != "0":
				dev_wlan = Dev("wlan", get_serial(a), get_id(a), get_name(a))
			elif "Wireless" in t and get_id(a) == "0":
				dev_wlan_internal = Dev("wlan", get_serial(a), get_id(a), get_name(a))
	return dev_eth, dev_wlan, dev_wlan_internal

def gui_get_devices(s):
	device_list = []
	arr = s.split("*-network")
	for a in arr:
		device_list.append(get_name(a))
	return device_list

def interfaces_scan():
	print("SCANNING HW NETWORK INTERFACES")
	p = Popen(['lshw','-class','network'], stdout=PIPE, stderr=PIPE)
	data, error = p.communicate()
	data = str(data)
	dev_eth, dev_wlan, dev_wlan_internal = get_devices(data)
	print("THE LOGICAL NAME OF THE INTERNAL WIRELESS INTERFACE IS:", dev_wlan_internal.name)
	print("THE LOGICAL NAME OF THE ETHERNET INTERFACE IS:", dev_eth.name)
	print("THE MAC ADDRESS OF THE ETHERNET INTERFACE IS:", dev_eth.mac_addr)
	print("THE LOGICAL NAME OF THE WIRELSS INTERFACE IS:", dev_wlan.name)
	print("THE MAC ADDRESS OF THE WIRELESS INTERFACE IS:", dev_wlan.mac_addr)

	return dev_eth.name, dev_eth.mac_addr, dev_wlan.name, dev_wlan.mac_addr, dev_wlan_internal.name

def gui_interfaces_scan():
	devices_list = []
	print("SCANNING HW NETWORK INTERFACES")
	p = Popen(['lshw','-class','network'], stdout=PIPE, stderr=PIPE)
	data = p.communicate()
	data = str(data)
	dev_list = gui_get_devices(data)
	print(dev_list)

	return dev_list
