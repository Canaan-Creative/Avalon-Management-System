#!/usr/bin/env python
from __future__ import print_function
import telnetlib
import sys
import time

import paramiko


def version_ssh(ip):
    passwd = 'PASSWORD'
    v = None
    retry = 3
    for i in range(0, retry):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        for k in range(0, retry):
            try:
                ssh.connect(ip, 22, 'root', passwd)
                break
            except:
                ssh.close()
                if k == retry - 1:
                    return None
        try:
            stdin, stdout, stderr = ssh.exec_command(
                'opkg list | grep ^cgminer | cut -c11-')
            time.sleep(2)
            v = stdout.read().split('\n')[0]
        except:
            ssh.close()
            continue

        ssh.close()
        break
    return v


def version(ip):
    v = None
    retry = 3
    flag = "root@OpenWrt:/# "
    for i in range(0, retry):
        tn = telnetlib.Telnet()
        for k in range(0, retry):
            # try connecting for some times
            try:
                tn.open(ip, 23)
                break
            except:
                tn.close()
                if k == retry - 1:
                    return None
        try:
            tn.read_until(flag)
            tn.write('opkg list | grep ^cgminer | cut -c11-\n')
            time.sleep(2)
            v = tn.read_until(flag)
            v = v.split("\n")[1]
            tn.write('exit\n')
            tn.read_all()
        except:
            tn.close()
            continue
        tn.close()
        break
    return v

if __name__ == '__main__':

    ip = sys.argv[1]
    v = version(ip)
    if v is None:
        v = version_ssh(ip)
    print(v)
