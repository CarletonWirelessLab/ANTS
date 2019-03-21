import re
from subprocess import *
class Cell:
    def __init__(self, e, f):
        self.essid = e
        self.frequency = f
    def __str__(self):
        return self.essid + ", " + self.frequency

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
            c = Cell(get_essid(a), get_frequency(a))
            if float(c.frequency) == float(fc):
                cells.append(c)
        index = index + 1
    return cells

def get_frequency_networks(device_name, center_frequency):
    print("BRINGING",device_name,"UP")
    call(['ifconfig', device_name, 'up'])
    call(['ip', 'addr', 'flush', 'dev', device_name])
    print("SCANNING NETWORKS ON THE WIRELESS INTERFACE", device_name, "FOR CENTER FREQUENCY", center_frequency)
    p = Popen(['iwlist', device_name, 'scan'], stdout=PIPE, stderr=PIPE)
    data, error = p.communicate()
    data = str(data)
    cells = get_frequency_cells(data, center_frequency)
    networks = []
    for c in cells:
        networks.append(c.essid)

    print('NETWORK SCAN COMPLETE')
    return networks
