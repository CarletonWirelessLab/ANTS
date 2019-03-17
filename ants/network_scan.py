import re
from subprocess import *
class Cell:
    def __init__(self, e, a):
        self.essid = e
        self.address = a
    def __str__(self):
        return self.essid + ", " + self.address

def get_address(s):
    m = re.search("Address: (([0-9A-Fa-f]{2}[:]){5})", s)
    if m:
        return m.group(1).lower()
    return None

# def get_level(s):
#     m = re.search("Signal level=(([0-9]{2}[:]){5})", s)
#     if m:
#         return m.group(1).lower()
#     return None


def get_essid(s):
    m = re.search("ESSID:\"(.*)\"", s)
    if m:
        return m.group(1)
    return None

def get_cells(s):
    cells = []
    arr = s.split("Cell")
    index = 0
    for a in arr:
        if index != 0:
            c = Cell(get_essid(a), get_address(a))
            cells.append(c)
        index = index + 1
    return cells

def match_address(arr,bridge_id):
    mx = 0
    index = 0
    i = 0
    for a in arr:
        if a.address in bridge_id:
            index = i
        i = i + 1
    return arr[index]

def get_all_networks(device_name):
    print("BRINGING",device_name,"UP")
    call(['ifconfig', device_name, 'up'])
    call(['ip', 'addr', 'flush', 'dev', device_name])
    print("SCANNING NETWORKS ON THE WIRELESS INTERFACE", device_name)
    p = Popen(['iwlist', device_name, 'scan'], stdout=PIPE, stderr=PIPE)
    data, error = p.communicate()
    data = str(data)
    cells = get_cells(data)
    networks = []
    # cells_sorted = sorted(cells, key=lambda x: x.level, reverse=True)
    for c in cells:
        networks.append(c.essid)

    print('NETWORK SCAN COMPLETE')
    return networks

def network_scan(device_name, bridge_id):
    print("SCANNING NETWORKS ON THE WIRELESS INTERFACE", device_name)
    p = Popen(['iwlist', device_name, 'scan'], stdout=PIPE, stderr=PIPE)
    data, error = p.communicate()
    data = str(data)
    cells = get_cells(data)
    c = match_address(cells,bridge_id)
    print("NETWORK ESSID", c.essid, "HAS A MATCHING ADDRESS{0}:xx".format(c.address))
    return c.essid
