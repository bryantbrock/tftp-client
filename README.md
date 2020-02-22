# tftp-client
A tftp client with minimal capabilities

1) Setup a test server (there is a built-in one running on mac under /private/tftpboot) 

2) Give the tftp client a command (either put or get a file to the host)
```
$ python3 tftp-client.py get test.txt
```
At this stage in the client, I found a python script written from the RFC 1350 <a href="https://smitsgit.github.io/blog/html/2018/06/13/tftp.html">here</a>

It had the ability to download the file and my goal was to give it the ability to upload a file. 

I figured it out, with the exception that you must create an empty file within the tftp server folder with the same name as the file you wish to upload. Give it "chmod 777" permissions and then you can upload the file.

The final goal will be to upload the file without having to first create it in the server. We shall see....

