
import socket
import sys
import argparse

parser = argparse.ArgumentParser(description="reads and writes a file to a server using TFTP protocol")

parser.add_argument("filename", help="the file you either want to read or write")
parser.add_argument("-r", "--read", help="read a file", action="store_true")
parser.add_argument("-w", "--write", help="write a file", action="store_true")

args = parser.parse_args()

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class Client():

    def __init__(self, filename):
        self.filename = filename

    def write(self):
        self.filename = (self.filename).encode('UTF-8')
        user = input('(type "default" for server running on localhost 10000)\nEnter address of host: ')

        def find_server(address='localhost', port=10000):
                server_address = (address, port)
                return server_address

        # Send data
        print('writing {!r}'.format(self.filename))
        if user == 'default':
            sent = sock.sendto(self.filename, find_server())
        else:
            sent = sock.sendto(self.filename, find_server(user.split(' ')[0], int(user.split(' ')[1])))
    
    def read(self):

        self.write()
        # Receive response
        print('waiting to read response...')
        data, server = sock.recvfrom(4)
        print('reading {!r}'.format(data))
        print('closing socket')
        sock.close()
        
if args.read:
    print("reading " + args.filename)
    reader = Client(args.filename)
    reader.read()
if args.write:
    print("writing " + args.filename)
    writer = Client(args.filename)
    writer.write()
    print('closing socket')
    sock.close()