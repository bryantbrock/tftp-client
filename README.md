# tftp-client
A tftp client with minimal capabilities

1) Setup a server ("default" is localhost 10000)
```
$ python3 tftpserver.py default --connect
```
Now that the server is up and running...

2) Give the tftp client a command (either read(-r) or write(-w) a message to the host)
```
$ python3 tftpclient.py -r "this is my message"
```
In this case, in order to read something from the host, you must first write it and then you can read it.
All of that is built in.
* You will see a prompt: ```(type "default" for server running on localhost 10000)
Enter address of host:```
* Enter address and you're done. 


