"""
tftp-client
Usage:
  tftp-client.py <action> <filename> [--port=<port> | --server=<server>]
  tftp-client.py (-h | --help)

Options:
  -h --help     Show this screen.
  --port=<port>            Use python struct to build request.
  --server=<server>            Use python bytearray to build request.
"""

from docopt import docopt
import socket
from struct import pack 

TFTP_OPCODES = {
    'unknown': 0,
    'read': 1,  # RRQ
    'write': 2,  # WRQ
    'data': 3,  # DATA
    'ack': 4,  # ACKNOWLEDGMENT
    'error': 5}  # ERROR

 #Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 69)


def send_rq(filename, action, server_address):
    request = bytearray()
    # First byte opcode 
    request.append(0)
    # Set specific request- second byte opcode
    if action == 'read':
        request.append(1)
    else:
        request.append(2)
    # append the filename you are interested in
    filename = bytearray(filename.encode('utf-8'))
    request += filename
    # append the null terminator
    request.append(0)
    # append the mode of transfer
    form = bytearray(bytes("octet", 'utf-8'))
    request += form
    # append the last byte
    request.append(0)

    print(f"Request {request}")
    sent = sock.sendto(request, server_address)

def send_data(ack_data, server):
    data = bytearray(ack_data)
    data[0] = 0
    data[1] = TFTP_OPCODES['data']
    bin_data = open('new.py', 'rb').read()
    data.append(bytearray(bin_data))
    print(data)
    sock.sendto(data, server)

def main():
    arguments = docopt(__doc__)
    filename = arguments['<filename>']
    action = arguments['<action>']
    print(arguments)
    # Set port of host
    if arguments['--port'] is not None:
        port = arguments['--port']
    else:
        port = 69
    # Set ip address of host
    if arguments['--server'] is not None:
        ip_address = arguments['--server']       
    else:
        ip_address = 'localhost'

    # Set server address
    server_address = (ip_address, port)
    # Send request
    send_rq(filename, action, server_address)


    # Open file locally with the same name as that of the requested file from server
    if action == "get":
        file = open(filename, "wb")

        while True:
            # Wait for the >>data<< from the server
            data, server = sock.recvfrom(600)

            
            send_ack(data[0:4], server)
            content = data[4:]
            # print(f"Content : {content}")
            file.write(content)
            # print(f"## Data ##: {data[0:4]} : {len(data)}")
            if len(data) < TERMINATING_DATA_LENGTH:
                break
    else:
        while True:
            # Wait for the >>ack<< from the server
            ack, server = sock.recvfrom(600)
            send_data(ack[0:4], server)
            break


            


if __name__ == '__main__':
    main()
