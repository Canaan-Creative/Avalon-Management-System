#!/usr/bin/env python2

from __future__ import print_function
import threading
import Queue
import socket
import json
import datetime
import re


def readAPI(ip, port, command, lock, retry):
    timeout = 0
    while True:
        timeout += 1
        if timeout > retry:
            return None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((ip, port))

            s.send(json.dumps({"command": command}))

            response = s.recv(4096)
            while True:
                recv = s.recv(4096)
                if not recv:
                    break
                else:
                    response += recv

            response = response.replace('\x00', '')
            s.close()
            result = json.loads(response)
            if command == 'summary':
                return result['SUMMARY'][0]
            elif command == 'edevs':
                return result['DEVS']
            elif command == 'estats':
                return result['STATS']
            elif command == 'pools':
                return result['POOLS']
            else:
                return result
        except:
            with lock:
                print("\033[31mConnection to " + ip + ":" + str(port) +
                      " lost. Extend time-out and try again.\033[0m")


def socketThread(minerQueue, dataQueue, lock, retry):
    while True:
        try:
            (minerID, monitor) = minerQueue.get(False)
        except Queue.Empty:
            break
        [ip, port] = minerID.split(":")
        port = int(port)

        failed = False
        for k in range(0, retry):
            # try connecting for some times
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(k + 1)
                s.connect((ip, 22))
                s.close()
                break
            except:
                s.close()
                if k < retry - 1:
                    with lock:
                        print('\033[1m\033[33mCannot connect to ' +
                              minerID + '. Try Again.\033[0m')
                else:
                    with lock:
                        print('\033[31mCannot connect to ' +
                              minerID + '. Skip.\033[0m')
                    failed = True

        if failed:
            data = {'IP': ip,
                    'Port': port,
                    'Alive': False,
                    'Summary': None,
                    'Devs': None,
                    'Stats': None,
                    'Pools': None,
                    'Monitor': None}

        else:
            devs = readAPI(ip, port, 'edevs', lock, retry * 2)
            stats = readAPI(ip, port, 'estats', lock, retry * 2)
            pools = readAPI(ip, port, 'pools', lock, retry * 2)
            summary = readAPI(ip, port, 'summary', lock, retry * 2)
            data = {'IP': ip,
                    'Port': port,
                    'Alive': True,
                    'Summary': summary,
                    'Devs': devs,
                    'Stats': stats,
                    'Pools': pools,
                    'Monitor': monitor}
            with lock:
                print("Complete fetching data from " + minerID + ".")

        dataQueue.put(data)
        minerQueue.task_done()


def readCgmonitorLog(fetchTime, cfg):

    api = re.compile("\S*\s(?P<ip>[.0-9]+)(:(?P<port>[0-9]+))?\s.*"
                     "api.*Elapsed=(?P<elapsed>.*),"
                     ".*MH=(?P<megahash>.*)$")
    if 'fetch_period' in cfg['General'] and not cfg['General']['fetch_period']:
        fetchTime0 = fetchTime - datetime.timedelta(
            seconds=int(cfg['General']['fetch_period']))
    else:
        fetchTime0 = datetime.datetime(1970, 1, 1)
    cgmonitorLog = {}

    with open(cfg['General']['cgmonitor_log'], 'r') as f:
        match = False
        for line in f:
            restartTime = datetime.datetime.strptime(
                line[:26], '%Y-%m-%dT%H:%M:%S.%f')
            if match or restartTime > fetchTime0:
                match = True
                if restartTime <= fetchTime:
                    m = re.search(api, line)
                    if m:
                        ip = m.group('ip')
                        port = m.group('port')
                        mid = "{}:{}".format(
                            ip,
                            port if port is not None else 4028)
                        elapsed = int(m.group('elapsed'))
                        megahash = float(m.group('megahash'))
                        if mid in cgmonitorLog:
                            monitor = cgmonitorLog[mid]
                            # There may be duplicated log entries,
                            # Reason: unknown bug of cgminer-monitor
                            if (restartTime - monitor['timestamp']).total_seconds() < elapsed - 1:
                                monitor['timestamp'] = restartTime
                                monitor['elapsed'] = elapsed
                                monitor['megahash'] = megahash
                            else:
                                monitor['timestamp'] = restartTime
                                monitor['elapsed'] += elapsed
                                monitor['megahash'] += megahash
                        else:
                            cgmonitorLog[mid] = {
                                'timestamp': restartTime,
                                'elapsed':  elapsed,
                                'megahash': megahash
                            }
                else:
                    break
    return cgmonitorLog


def collect(fetchTime, cfg):

    minerList = cfg['minerList']
    threadNum = int(cfg['Cgminer']['threadnum'])
    retry = int(cfg['Cgminer']['retry'])
    minerQueue = Queue.Queue()
    dataQueue = Queue.Queue()

    lock = threading.Lock()

    print("Reading cgmonitor log... ", end="")
    cgmonitorLog = {}
    if ('cgmonitor_log' in cfg['General'] and cfg['General']['cgmonitor_log']):
            cgmonitorLog = readCgmonitorLog(fetchTime, cfg)
    print("Done.")

    for miner in minerList:
        monitor = None
        if miner in cgmonitorLog:
            monitor = cgmonitorLog[miner]
        minerQueue.put((miner, monitor))

    for i in range(threadNum):
        t = threading.Thread(target=socketThread,
                             args=(minerQueue, dataQueue, lock, retry))
        t.daemon = True
        t.start()

    minerQueue.join()
    return dataQueue
