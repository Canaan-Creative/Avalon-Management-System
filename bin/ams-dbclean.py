#!/usr/bin/env python2

from __future__ import print_function
import datetime
import Queue
import threading
import os
import tarfile
import shutil

import MySQLdb

from configurate import configurate


def dbThread(tableQueue, user, passwd, dbname, folder, lock):

    db = MySQLdb.connect(host="localhost", user=user, passwd=passwd, db=dbname)
    c = db.cursor()
    while True:
        try:
            table = tableQueue.get(False)
        except:
            break
        try:
            c.execute("DESCRIBE {0}".format(table))
        except:
            tableQueue.task_done()
            continue
        result = c.fetchall()
        headers = ""
        for row in result:
            headers += "'{0}', ".format(row[0])

        c.execute("SELECT {2} UNION SELECT * FROM {0} INTO OUTFILE "
                  "'{1}.csv' FIELDS ENCLOSED BY '\"' TERMINATED BY ';' "
                  "ESCAPED BY '\"' LINES TERMINATED BY '\\n'"
                  .format(table, os.path.join(folder, table), headers[:-2]))
        c.execute("DROP TABLE {0}".format(table))
        db.commit()
        tableQueue.task_done()

    c.close()
    db.close()


def getTables(c, tableQueue, prefix, now):

    c.execute("SHOW TABLES LIKE '{0}\_%'".format(prefix))
    result = c.fetchall()
    if result is None:
        exit()
    starttime = result[0][0][(len(prefix) + 1):]
    for row in result:
        time = row[0][(len(prefix) + 1):]
        t = datetime.datetime.strptime(time, '%Y_%m_%d_%H_%M')
        if t > now - datetime.timedelta(seconds=24 * 3600):
            break
        endtime = time
        tableQueue.put(row[0])

    return (starttime, endtime)


if __name__ == '__main__':

    cfg = configurate('../etc/ams.conf')
    now = datetime.datetime.now()
    now_s = '{:%Y_%m_%d_%H_%M}'.format(now)

    threadNum = int(cfg['Database']['threadnum'])
    user = cfg['Database']['user']
    passwd = cfg['Database']['passwd']
    dbname = cfg['Database']['dbname']

    tableQueue = Queue.Queue()

    db = MySQLdb.connect(host="localhost", user=user, passwd=passwd, db=dbname)
    c = db.cursor()

    (starttime, endtime) = getTables(c, tableQueue, 'Miner', now)
    getTables(c, tableQueue, 'Device', now)
    getTables(c, tableQueue, 'Module', now)
    getTables(c, tableQueue, 'Pool', now)
    getTables(c, tableQueue, 'Error', now)

    db.commit()
    c.close()
    db.close()

    folder = os.path.join(cfg['Folder']['archive'], 'archive')

    try:
        os.mkdir(folder)
    except:
        pass
    os.chmod(folder, 0777)

    lock = threading.Lock()

    for i in range(threadNum):
        t = threading.Thread(target=dbThread,
                             args=(tableQueue, user, passwd,
                                   dbname, folder, lock))
        t.daemon = True
        t.start()
    tableQueue.join()

    tarPath = os.path.join(cfg['Folder']['archive'],
                           '{0}__{1}.tar.bz2'.format(starttime, endtime))
    with tarfile.open(tarPath, "w:bz2") as tar:
        tar.add(folder, arcname=os.path.basename(folder))

    shutil.rmtree(folder)
