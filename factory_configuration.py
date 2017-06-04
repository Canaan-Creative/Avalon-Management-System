#!/usr/bin/env python
import threading
import Queue
import socket
import sys
from cgminer_api import cgminer_api


def socketthread(miner_queue):
    while True:
        try:
            m = miner_queue.get(False)
            ms = m.split(',')
            ip = ms[0]
            port = ms[1]
            value = ms[2]

            devs = cgminer_api(ip, port, ['edevs'])
            try:
                dev = devs.items()[1]
                for i, val in enumerate(dev[1]):
                    did = val.items()[0][1]
                    cgminer_api(ip, port,
                            ['ascset', '{},factory,{}'.format(did, value)])
            except:
                print ip + " " + port + " " + "devs can't found";

            miner_queue.task_done()

        except Queue.Empty:
            break


if __name__ == '__main__':

    retry = 1
    threads_n = 100

    modules = sys.argv[1:]

    module_queue = Queue.Queue()

    for m in modules:
        module_queue.put(m)

    threads = []

    for i in range(0, threads_n):
        t = threading.Thread(
            target=socketthread, args=(module_queue, ))
        t.daemon = True
        t.start()

    module_queue.join()
