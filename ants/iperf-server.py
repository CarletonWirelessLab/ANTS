from iperf3 import *

def main():
	server = iperf3.Server()
	server.port = 5201
	server.bind_address = "10.1.1.12"
	while True:
		result = server.run()

if __name__ == '__main__':
	main()
