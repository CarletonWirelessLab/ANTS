#!/bin/bash

# ifconfig enxe84e065d4aff 10.1.1.120 netmask 255.255.255.0
# ifconfig enp2s0f1 10.1.11.115 netmask 255.255.255.0

echo "This script will set up the network routing required to test on a single machine."
echo "Alternatively, you can press CTRL+C to stop the script and manually configure your network interfaces."
echo
echo "Which network interface would you like to use for the iperf server address?"

ip_interfaces="$(ip -o link show | awk -F': ' '{print $2}')"

lo_interface="lo"

new_array=()
for value in "${ip_interfaces[@]}"
do
    [[ $value != $lo_interface ]] && new_array+=($value)
done
ip_interfaces=("${new_array[@]}")
unset new_array

for ((i = 0; i < ${#ip_interfaces[@]}; ++i)); do
    # bash arrays are 0-indexed
    position=$(( $i + 1 ))
    echo "$position: ${ip_interfaces[$i]}"
done

while true; do
  read -p "Input a device number, then press ENTER: " server_dev

  case server_dev in
    [1]* ) server_device=${ip_interfaces[1]}; break;;
        [Nn]* ) break;;
        * ) echo "Please answer yes or no.";;
    esac
done

# ip addr add 10.1.1.120/24 dev enxe84e065d4aff
# ip addr add 10.1.11.115/24 dev enp2s0f1
# iptables -t nat -L
# iptables -t nat -A POSTROUTING -s 10.1.1.120 -d 10.2.11.115 -j SNAT --to-source 10.2.1.120
# iptables -t nat -A PREROUTING -d 10.2.1.120 -j DNAT --to-destination 10.1.1.120
# iptables -t nat -A POSTROUTING -s 10.1.11.115 -d 10.2.1.120 -j SNAT --to-source 10.2.11.115
# iptables -t nat -A PREROUTING -d 10.2.11.115 -j DNAT --to-destination 10.1.11.115
#
# ip route add 10.2.11.115 dev enxe84e065d4aff
# arp -i enxe84e065d4aff -s 10.2.11.115 80:ce:62:2a:b1:e5 # enp2s0f1's mac address
#
# ip route add 10.2.1.120 dev enp2s0f1
# arp -i enp2s0f1 -s 10.2.1.120 e8:4e:06:5d:4a:ff # enxe84e065d4aff's mac address

# iperf -B 10.1.1.120 -s -u -t 1000000000000000 -i 1 &
# iperf -B 10.1.11.115 -c 10.2.1.120 -u -b 150M -t 10000000000000 -i 1 -S 0xC0 > /dev/null 2>&1
