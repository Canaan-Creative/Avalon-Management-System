#!/usr/bin/env python
import socket
import json
import sys
import string


def linesplit(socket):
    buffer = socket.recv(4096)
    while True:
        more = socket.recv(4096)
        if not more:
            break
        else:
            buffer = buffer+more
    if buffer:
        return buffer

api_command = sys.argv[1].split('|')

if len(sys.argv) < 3:
    api_ip = '127.0.0.1'
    api_port = 4028
else:
    api_ip = sys.argv[2]
    api_port = sys.argv[3]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((api_ip, int(api_port)))
if len(api_command) == 2:
    s.send(json.dumps({"command": api_command[0], "parameter": api_command[1]}))
else:
    s.send(json.dumps({"command": api_command[0]}))

response = linesplit(s)
s.close()

response = ''.join(filter(lambda x: x in string.printable, response))
temp = list(response)
for i in range(1, len(temp) - 1):
    if temp[i] == '"' and (
            temp[i - 1] != ':' and temp[i - 1] != ',' and
            temp[i - 1] != '{' and temp[i + 1] != ':' and
            temp[i + 1] != ',' and temp[i + 1] != '}'):
        temp[i] = ''
response = ''.join(temp)
print json.loads(response)
