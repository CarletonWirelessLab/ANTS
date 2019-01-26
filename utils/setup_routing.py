import os
import subprocess

server_device_name = None
server_device_mac = None
server_ip = "10.1.1.120"
client_device_name = None
client_device_mac = None
client_ip = "10.1.11.115"

state = True

device_list = os.listdir("/sys/class/net")
device_list.remove("lo")

print("This script will configure the units under test for operation from a single machine.\n")
print("Alternatively, you may stop this script and set up your network devices manually, using this script as a guide.\n")
print("Note that it assumes that your network devices will be able to use the IP addresses 10.1.1.120 and 10.1.11.115.\n")

print(device_list)

while state == True:
    print("Which of the following devices would you like to use for the iperf server?\n")
    for value in range(0, len(device_list)):
        print("{0}: {1}\n".format(value, device_list[value]))
    selection = int(input("Select a device number: "))
    if selection in range(0, len(device_list)):
        server_device_name = device_list[selection]
        print(server_device_name)
        device_list.remove(device_list[selection])
        state = False
    else:
        print("Bad input. Try again.\n")

state = True

while state == True:
    print("Which of the following devices would you like to use for the iperf client?\n")
    for value in range(0, len(device_list)):
        print("{0}: {1}\n".format(value, device_list[value]))
    selection = int(input("Select a device number: "))
    if selection in range(0, len(device_list)):
        client_device_name = device_list[selection]
        print(client_device_name)
        state = False
    else:
        print("Bad input. Try again.\n")

print("{0} and {1} will now be configured for routing.\n".format(server_device_name, client_device_name))
with open("/sys/class/net/{0}/address".format(server_device_name)) as f:
    server_device_mac = f.readline().rstrip("\n")
with open("/sys/class/net/{0}/address".format(client_device_name)) as f:
    client_device_mac = f.readline().rstrip("\n")

print("Server device MAC address is {0}\n".format(server_device_mac))
print("Client device MAC address is {0}\n".format(client_device_mac))

print("Setting up IP addresses...\n")

server_ip_args = "ip addr add {0}/24 dev {1}".format(server_ip, server_device_name).split(" ")
client_ip_args = "ip addr add {0}/24 dev {1}".format(client_ip, client_device_name).split(" ")

iptables_one_args = "iptables -t nat -L".split(" ")
iptables_two_args = "iptables -t nat -A POSTROUTING -s {0} -d 10.2.11.115 -j SNAT --to-source 10.2.1.120".format(server_ip).split(" ")
iptables_three_args = "iptables -t nat -A PREROUTING -d 10.2.1.120 -j DNAT --to-destination {0}".format(server_ip).split(" ")
iptables_four_args = "iptables -t nat -A POSTROUTING -s {0} -d 10.2.1.120 -j SNAT --to-source 10.2.11.115".format(client_ip).split(" ")
iptables_five_args = "iptables -t nat -A PREROUTING -d 10.2.11.115 -j DNAT --to-destination {0}".format(client_ip).split(" ")

ip_route_one_args = "ip route add 10.2.11.115 dev {0}".format(server_device_name).split(" ")
arp_one_args = "arp -i {0} -s 10.2.11.115 {1}".format(server_device_name, client_device_mac).split(" ")

ip_route_two_args = "ip route add 10.2.1.120 dev {0}".format(client_device_name).split(" ")
arp_two_args = "arp -i {0} -s 10.2.1.120 {1}".format(client_device_name, server_device_mac).split(" ")

subprocess.call(server_ip_args)
subprocess.call(client_ip_args)
subprocess.call(iptables_one_args)
subprocess.call(iptables_two_args)
subprocess.call(iptables_three_args)
subprocess.call(iptables_four_args)
subprocess.call(iptables_five_args)

subprocess.call(ip_route_one_args)
subprocess.call(arp_one_args)
subprocess.call(ip_route_two_args)
subprocess.call(arp_two_args)

print("Network routing should now be ready for use with ANTS.\n")
