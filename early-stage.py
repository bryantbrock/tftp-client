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

server_error_msg = {
    0: "Not defined, see error message (if any).",
    1: "File not found.",
    2: "Access violation.",
    3: "Disk full or allocation exceeded.",
    4: "Illegal TFTP operation.",
    5: "Unknown transfer ID.",
    6: "File already exists.",
    7: "No such user."
}

TFTP_OPCODES = {
    'unknown': 0,
    'read': 1,  # RRQ
    'write': 2,  # WRQ
    'data': 3,  # DATA
    'ack': 4,  # ACKNOWLEDGMENT
    'error': 5}  # ERROR

 #Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('172.20.10.3', 69)

def server_error(data):
    opcode = data[:2]
    return int.from_bytes(opcode, byteorder='big') == TFTP_OPCODES['error']


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

def send_ack(ack_data, server):
    ack = bytearray(ack_data)
    ack[0] = 0
    ack[1] = TFTP_OPCODES['ack']
    print(ack)
    sock.sendto(ack, server)

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

            if server_error(data):
                error_code = int.from_bytes(data[2:4], byteorder='big')
                print(server_error_msg[error_code])
                break
            send_ack(data[0:4], server)
            content = data[4:]
            # print(f"Content : {content}")
            file.write(content)
            # print(f"## Data ##: {data[0:4]} : {len(data)}")
            if len(data) < 516:
                break
    if action == "put":
        while True:
            # Wait for the >>ack<< from the server
            ack, server = sock.recvfrom(600)
            print(ack)

            if server_error(ack):
                error_code = int.from_bytes(ack[2:4], byteorder='big')
                print(server_error_msg[error_code])
                break
            print('Yay!')
            break


            


if __name__ == '__main__':
    main()
