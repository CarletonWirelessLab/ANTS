#!/bin/bash
ifconfig enxe84e065d4aff 10.1.1.120 netmask 255.255.255.0
ifconfig enp2s0f1 10.1.11.115 netmask 255.255.255.0
iptables -t nat -L
iptables -t nat -A POSTROUTING -s 10.1.1.120 -d 10.2.11.115 -j SNAT --to-source 10.2.1.120
iptables -t nat -A PREROUTING -d 10.2.1.120 -j DNAT --to-destination 10.1.1.120
iptables -t nat -A POSTROUTING -s 10.1.11.115 -d 10.2.1.120 -j SNAT --to-source 10.2.11.115
iptables -t nat -A PREROUTING -d 10.2.11.115 -j DNAT --to-destination 10.1.11.115

ip route add 10.2.11.115 dev enxe84e065d4aff
arp -i enxe84e065d4aff -s 10.2.11.115 80:ce:62:2a:b1:e5 # enp2s0f1's mac address 

ip route add 10.2.1.120 dev enp2s0f1
arp -i enp2s0f1 -s 10.2.1.120 e8:4e:06:5d:4a:ff # enxe84e065d4aff's mac address

iperf -B 10.1.1.120 -s -u -t 1000000000000000 -i 1 &
iperf -B 10.1.11.115 -c 10.2.1.120 -u -b 150M -t 10000000000000 -i 1 -S 0xC0 > /dev/null 2>&1


