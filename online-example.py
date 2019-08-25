"""
tftp-client.
Usage:
  tftp-client.py get <filename> [[-s | -b ] --mode=<mode>]
  tftp-client.py (-h | --help)

Options:
  -h --help     Show this screen.
  -s            Use python struct to build request.
  -b            Use python bytearray to build request.
  --mode=<mode> TFTP transfer mode : "netascii", "octet", or "mail"
"""

from docopt import docopt
import socket
from struct import pack

"""
    opcode  operation
     1     Read request (RRQ)
     2     Write request (WRQ)
     3     Data (DATA)
     4     Acknowledgment (ACK)
     5     Error (ERROR)

>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

      2 bytes     string    1 byte     string   1 byte
     ------------------------------------------------
    | Opcode |  Filename  |   0  |    Mode    |   0  |
     ------------------------------------------------

    Figure 5-1: RRQ/WRQ packet

   The [[ Mode ]] field contains the

   string "netascii", "octet", or "mail" (or any combination of upper
   and lower case, such as "NETASCII", NetAscii", etc.)


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

      2 bytes     2 bytes
     ---------------------
    | Opcode |   Block #  |
     ---------------------

     Figure 5-3: ACK packet

>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

      2 bytes     2 bytes      n bytes
     ----------------------------------
    | Opcode |   Block #  |   Data     |
     ----------------------------------

     Figure 5-2: DATA packet
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

TFTP Formats

   Type   Op #     Format without header

          2 bytes    string   1 byte     string   1 byte
          -----------------------------------------------
   RRQ/  | 01/02 |  Filename  |   0  |    Mode    |   0  |
   WRQ    -----------------------------------------------


          2 bytes    2 bytes       n bytes
          ---------------------------------
   DATA  | 03    |   Block #  |    Data    |
          ---------------------------------


          2 bytes    2 bytes
          -------------------
   ACK   | 04    |   Block #  |
          --------------------


          2 bytes  2 bytes        string    1 byte
          ----------------------------------------
   ERROR | 05    |  ErrorCode |   ErrMsg   |   0  |
          ----------------------------------------

Error Codes

   Value     Meaning

   0         Not defined, see error message (if any).
   1         File not found.
   2         Access violation.
   3         Disk full or allocation exceeded.
   4         Illegal TFTP operation.
   5         Unknown transfer ID.
   6         File already exists.
   7         No such user.

====================
Protocol in action
====================

As shown above the protocol can be seen in action on the last 6 lines or so.

1. Client sends a Read Request specifying a file and mode. [ We can see opcodes for that in RFC ]
2. Server responds with block of data along with block number.
3. Client sends an ACK for the received block
4. Server sends next data with incremented block number and ......

** Normal Termination ** - This excerpt is taken directly from `RFC 1350 <https://tools.ietf.org/html/rfc1350/>`_
  The end of a transfer is marked by a DATA packet that contains
  between 0 and 511 bytes of data (i.e., Datagram length < 516).  This
  packet is acknowledged by an ACK packet like all other DATA packets.
  The host acknowledging the final DATA packet may terminate its side
  of the connection on sending the final ACK.

"""
TERMINATING_DATA_LENGTH = 516
TFTP_TRANSFER_MODE = b'netascii'

TFTP_OPCODES = {
    'unknown': 0,
    'read': 1,  # RRQ
    'write': 2,  # WRQ
    'data': 3,  # DATA
    'ack': 4,  # ACKNOWLEDGMENT
    'error': 5}  # ERROR

TFTP_MODES = {
    'unknown': 0,
    'netascii': 1,
    'octet': 2,
    'mail': 3}

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 69)


def send_rq(filename, mode):
    """
    This function constructs the request packet in the format below.
    Demonstrates how we can construct a packet using bytearray.

        Type   Op #     Format without header

               2 bytes    string   1 byte     string   1 byte
               -----------------------------------------------
        RRQ/  | 01/02 |  Filename  |   0  |    Mode    |   0  |
        WRQ    -----------------------------------------------


    :param filename:
    :return:
    """
    request = bytearray()
    # First two bytes opcode - for read request
    request.append(0)
    request.append(2)
    # append the filename you are interested in
    filename = bytearray(filename.encode('utf-8'))
    request += filename
    # append the null terminator
    request.append(0)
    # append the mode of transfer
    form = bytearray(bytes(mode, 'utf-8'))
    request += form
    # append the last byte
    request.append(0)

    print(f"Request {request}")
    sent = sock.sendto(request, server_address)


def send_rq_struct(filename, mode):
    """
    This function constructs the request packet in the format below
    Demonstrates how we can construct a packet using struct.

        Type   Op #     Format without header
               2 bytes    string   1 byte     string   1 byte
               -----------------------------------------------
        RRQ/  | 01/02 |  Filename  |   0  |    Mode    |   0  |
        WRQ    -----------------------------------------------

        :param filename:
        :return:
    """
    formatter = '>h{}sB{}sB'  # { > - Big Endian, h - short , s - char, B - 1 byte }
    formatter = formatter.format(len(filename), len('netascii'))
    print(formatter)  # final format '>h8sB8sB'
    request = pack(formatter, TFTP_OPCODES['read'], bytes(filename, 'utf-8'), 0, bytes(mode, 'utf-8'), 0)

    print(f"Request {request}")
    sent = sock.sendto(request, server_address)


def send_ack(ack_data, server):
    """
    This function constructs the ack using the bytearray.
    We dont change the block number cause when server sends data it already has
    block number in it.

              2 bytes    2 bytes
             -------------------
      ACK   | 04    |   Block #  |
             --------------------
    :param ack_data:
    :param server:
    :return:
    """
    ack = bytearray(ack_data)
    ack[0] = 0
    ack[1] = TFTP_OPCODES['ack']
    print(ack)
    sock.sendto(ack, server)


def server_error(data):
    """
    We are checking if the server is reporting an error
                2 bytes  2 bytes        string    1 byte
              ----------------------------------------
       ERROR | 05    |  ErrorCode |   ErrMsg   |   0  |
              ----------------------------------------
    :param data:
    :return:
    """
    opcode = data[:2]
    return int.from_bytes(opcode, byteorder='big') == TFTP_OPCODES['error']


# Map server error codes to messages [ Taken from RFC-1350 ]
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


def main():
    arguments = docopt(__doc__)
    filename = arguments['<filename>']
    print(arguments)
    if arguments['--mode'] is not None:
        mode = arguments['--mode']
        if mode.lower() not in TFTP_MODES.keys():
            print("Unknown mode - defaulting to [ netascii ]")
            mode = "netascii"
    else:
        mode = "netascii"

    # Send request
    if arguments['-s']:
        send_rq_struct(filename, mode)
    elif arguments['-b']:
        send_rq(filename, mode)
    else:
        send_rq_struct(filename)

    # Open file locally with the same name as that of the requested file from server
    file = open(filename, "wb")
    while True:
        # Wait for the data from the server
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
        if len(data) < TERMINATING_DATA_LENGTH:
            break


if __name__ == '__main__':
    main()
