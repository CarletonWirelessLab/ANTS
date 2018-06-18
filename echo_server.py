#!/bin/python3

import socket
import sys
from datetime import datetime

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 5025)
print('starting up on {0} port {1}'.format(*server_address))
sock.bind(server_address)

sock.listen(5)

while True:
    print("\n")
    #print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        #print('connection from', client_address)

        while True:
            data = connection.recv(255)
            print("Received \"{0}\"".format(data))
            #print("received \"{0}\"".format(data.decode()))

            if data:
                pass
            else:
                break
    finally:
        connection.close()
