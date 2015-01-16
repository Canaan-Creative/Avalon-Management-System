#!/usr/bin/env python
import threading
import Queue
import socket
import sys
from cgminer_api import cgminer_api


def apiread(ip, port, command, retry):
    time_out = 0
    while True:
        time_out += 1
        if time_out > retry:
            return None
        try:
            return cgminer_api(ip, port, command)
        except:
            pass


def socketthread(miner_queue, data, lock, retry):
    while True:
        try:
            (ip, port, did, mid) = miner_queue.get(False)

            err_conn_flag = False
            for k in range(0, retry):
                # try connecting for some times
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(1)
                    s.connect((ip, int(port)))
                    s.close()
                    break
                except:
                    s.close()
                    err_conn_flag = True

            if err_conn_flag:
                continue

            else:
                apiread(ip, port,
                        ['ascset', '{},led,{}'.format(did, mid)],
                        retry)

        except Queue.Empty:
            break


if __name__ == '__main__':

    retry = 3
    threads_n = 100

    modules = sys.argv[1:]

    module_queue = Queue.Queue()

    for m in modules:
        module_queue.put(m.split(','))

    threads = []

    for i in range(0, threads_n):
        t = threading.Thread(
            target=socketthread, args=(module_queue, retry))
        t.daemon = True
        t.start()

    module_queue.join()
