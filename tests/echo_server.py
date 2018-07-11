#!/bin/python3

import socket
import sys
import time
import datetime

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
date = str(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

server_address = ('localhost', 5025)
print('starting up on {0} port {1}'.format(*server_address))
print('Started running at time: {0}'.format(date))
sock.bind(server_address)

sock.listen(5)

while True:
    print("\n")
    connection, client_address = sock.accept()
    try:

        while True:
            data = connection.recv(255)
            cur_time = str(datetime.datetime.utcnow().strftime("%H:%M:%S"))
            print("{0}: Received \"{1}\"".format(cur_time, data))

            if data:
                pass
            else:
                break
    finally:
        connection.close()
