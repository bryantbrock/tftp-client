
import socket
import sys
import argparse

parser = argparse.ArgumentParser(description="reads and writes a file to a server using TFTP protocol")
parser.add_argument('address', metavar='N', nargs='+',help='address of the host server')
parser.add_argument('--connect',action='store_true',help='make a connection to a port ([address] [port] --connect)')
args = parser.parse_args()

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def bind_socket_to_port(address='localhost', port=10000):
    # Bind the socket to the port
    server_address = (address, port)
    print('starting up on {} port {}'.format(*server_address))
    sock.bind(server_address)

if args.connect:
    if args.address[0] == 'default':
        bind_socket_to_port()
    else:
        print(args.address)
        print(args.address)
        bind_socket_to_port(address=args.address[0], port=int(args.address[1]))

while True:
    print('\nwaiting to receive message')
    data, address = sock.recvfrom(4096)

    print('received {} bytes from {}'.format(
        len(data), address))
    print(data)

    if data:
        sent = sock.sendto(data, address)
        print('sent {} bytes back to {}'.format(
            sent, address))