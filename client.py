#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import os, sys
from configparser import ConfigParser

config = ConfigParser()
config.read(sys.argv[1])

socket_name = config.get('BOT', 'name')

print("Connecting...")
if os.path.exists(f"/tmp/{socket_name}"):
    client = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
    client.connect(f"/tmp/{socket_name}")
    print("Ready.")
    print("Ctrl-C to quit.")
    print("Sending 'DONE' shuts down the server and quits.")
    while True:
       try:
            x = input( "> " )
            if x:
                if x.upper() == 'DONE':
                    print("Shutting down.")
                    break
                print("SEND:", x)
                client.send(x.encode('UTF-8'))
       except KeyboardInterrupt:
           print("Shutting down.")
    client.close()
else:
    print("Couldn't Connect!")
