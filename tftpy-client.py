"""
tftp-client
Usage:
  tftp-client.py <action> <filename> <server> <port> 
  tftp-client.py (-h | --help)

Options:
  -h --help     Show this screen.
  --port=69            Use python struct to build request.
  --server=<server>            Use python bytearray to build request.
"""

from docopt import docopt
import socket
import tftpy

def main():
    arguments = docopt(__doc__)
    action = arguments['<action>']
    print(arguments)
    client = tftpy.TftpClient(arguments['<server>'], int(arguments['<port>']))
    if action == 'get':
        client.download(arguments['<filename>'], arguments['<filename>'])
    if action == 'put':
        # client.upload(arguments['<filename>'], open('test.txt', 'rb', buffering=0)) -- Broken module in TftpClient Class
        exit()

if __name__ == '__main__':
    main()

