import re
from subprocess import *

class Cell:
    def __init__(self, cellDescription):
        self._cellDescription = cellDescription
        self.essid = self.get_essid()
        self.frequency = self.get_frequency()
        self.is_encrypted = self.get_encrypted()

    def __str__(self):
        return self.essid + ", " + self.frequency

    def get_frequency(self):
        m = re.search("Frequency:([0-9][.][0-9]*) GHz", self._cellDescription)
        if m:
            return m.group(1)
        return None

    def get_encrypted(self):
        m = re.search("Encryption key:on", self._cellDescription)
        if m:
            return True
        return False

    def get_essid(self):
        m = re.search("ESSID:\"(.*)\"", self._cellDescription)
        if m:
            return m.group(1)
        return None

def get_frequency_cells(s, selectedFrequency):
    cells = []
    cellDescriptions = s.split("Cell")
    index = 0
    for cellDescription in cellDescriptions:
        if index == 0:
            break
        c = Cell(cellDescription)
        if float(c.frequency) == float(selectedFrequency) and c.is_encrypted == False:
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
