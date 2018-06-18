#!/bin/python3

import socket
import sys

def echo_to_server(message="default output message", port=5025):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('localhost', port)

    print("Connecting to {0}:{1}".format(*server_address))
    sock.connect(server_address)

    try:

        echo_message = message
        print("Sending {0}".format(echo_message))
        sock.sendall(echo_message.encode())

    finally:
        print("Closing socket\n")
        sock.close()

if __name__ == '__main__':
    #echo_to_server(sys.argv[1])
    #print(sys.argv[1])
    echo_to_server(sys.argv[1])
