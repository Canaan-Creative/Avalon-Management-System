#!/usr/bin/env python
import socket
import json
import sys
import string
from collections import OrderedDict


def linesplit(socket):
    buffer = socket.recv(4096)
    while True:
        more = socket.recv(4096)
        if not more:
            break
        else:
            buffer = buffer + more
    if buffer:
        return buffer


def cgminer_api(ip, port, command):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, int(port)))
    if len(command) == 2:
        s.send(json.dumps({"command": command[0], "parameter": command[1]}))
    else:
        s.send(json.dumps({"command": command[0]}))

    response = linesplit(s)
    s.close()

    response = ''.join(filter(lambda x: x in string.printable, response))
    temp = list(response)
    for i in range(1, len(temp) - 1):
        if temp[i] == '\\' or (
                temp[i] == '"' and
                temp[i - 1] != ':' and temp[i - 1] != ',' and
                temp[i - 1] != '{' and temp[i + 1] != ':' and
                temp[i - 1] != '[' and temp[i + 1] != ']' and
                temp[i + 1] != ',' and temp[i + 1] != '}'):
            temp[i] = ''
    response = ''.join(temp)
    return json.loads(response, object_pairs_hook=OrderedDict)


if __name__ == '__main__':
    command = sys.argv[1].split('|')

    if len(sys.argv) < 3:
        ip = '127.0.0.1'
        port = 4028
    else:
        ip = sys.argv[2]
        port = sys.argv[3]

    print cgminer_api(ip, port, command)
