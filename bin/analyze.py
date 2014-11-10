#!/usr/bin/env python2

import MySQLdb
import threading
import Queue
from datetime import datetime


def dbThread(dataQueue, user, passwd, dbname, timenow, time0,
             volt0, devNumDict, modNumDict, lock):

    db = MySQLdb.connect(host="localhost", user=user, passwd=passwd, db=dbname)
    c = db.cursor()
    while True:
        try:
            data = dataQueue.get(False)
        except Queue.Empty:
            break

        command = ["INSERT INTO Miner_" + timenow + " VALUES(" +
                   ("%s," * 15)[:-1] + ")",
                   "INSERT INTO Device_" + timenow + " VALUES(" +
                   ("%s," * 5)[:-1] + ")",
                   "INSERT INTO Module_" + timenow + " VALUES(" +
                   ("%s," * 12)[:-1] + ")",
                   "INSERT INTO Pool_" + timenow + " VALUES(" +
                   ("%s," * 6)[:-1] + ")",
                   "INSERT INTO Error_" + timenow + " VALUES(" +
                   ("%s," * 15)[:-1] + ")"]
        ip = data['IP']
        port = data['Port']
        minerid = '{0}:{1}'.format(ip, port)

        try:
            sumdevice0 = devNumDict[minerid]
        except:
            sumdevice0 = 0
        try:
            summodule0 = modNumDict[minerid]
        except:
            summodule0 = 0

        deviceParam = []
        moduleParam = []
        poolParam = []
        errorParam = []

        if time0 is not None:
            c.execute("SELECT elapsed, megahash, block, newblock FROM Miner_{0}"
                      " WHERE ip = %s AND port = %s".format(time0), (ip, port))
            result = c.fetchall()
            if result:
                (elapsed0, megahash0, block0, newblock0) = result[0]
                t0 = datetime.strptime(time0, '%Y_%m_%d_%H_%M')
                t = datetime.strptime(timenow, '%Y_%m_%d_%H_%M')
                deltatime = (t - t0).total_seconds()
            else:
                elapsed0 = 0
                megahash0 = 0.0
                block0 = 0
                newblock0 = 0
                deltatime = 0
        else:
            # First time running.
            elapsed0 = 0
            megahash0 = 0.0
            block0 = 0
            newblock0 = 0
            deltatime = 0

        elapsed = 0
        megahash = .0

        if data['Monitor'] is not None:
            elapsed = data['Monitor']['elapsed']
            megahash = data['Monitor']['megahash']

        if not data['Alive']:
            try:
                if elapsed - elapsed0 > deltatime - 120:
                    rate1hr = (megahash - megahash0) / deltatime
                else:
                    rate1hr = megahash / deltatime
            except:
                rate1hr = .0
            minerParam = (ip, port, False, 0, sumdevice0, 0, summodule0,
                          0, 0, block0 + newblock0, 0, 0, rate1hr, .0, 0)
            errorParam.append(
                (ip, port, 0, 0, True, False, False, False,
                 False, False, False, False, False, False, False)
            )
        elif data['Summary'] is None:
            try:
                if elapsed - elapsed0 > deltatime - 120:
                    rate1hr = (megahash - megahash0) / deltatime
                else:
                    rate1hr = megahash / deltatime
            except:
                rate1hr = .0
            minerParam = (ip, port, True, 0, sumdevice0, 0, summodule0,
                          0, 0, block0 + newblock0, 0, 0, rate1hr, .0, 0)
            errorParam.append(
                (ip, port, 0, 0, False, sumdevice0, False, False,
                 False, False, False, False, False, False, False)
            )
        else:
            sumdevice = len(data['Devs'])
            elapsed += int(data['Summary']['Elapsed'])
            megahash += float(data['Summary']['Total MH'])
            rate15min = float(data['Summary']['MHS 15m'])
            newblock = int(data['Summary']['Found Blocks'])

            if sumdevice < sumdevice0:
                errorParam.append(
                    (ip, port, 0, 0, False, sumdevice0 - sumdevice, False,
                     False, False, False, False, False, False, False, False)
                )

            try:
                if elapsed - elapsed0 > deltatime - 120:
                    rate1hr = (megahash - megahash0) / deltatime
                else:
                    rate1hr = megahash / deltatime
            except:
                rate1hr = .0

            # TODO: read rpi.log for block
            if newblock < newblock0:
                newfoundblock = newblock
                block = block0 + newblock0
            else:
                newfoundblock = newblock - newblock0
                block = block0

            if newfoundblock != 0:
                c.execute("CREATE TABLE IF NOT EXISTS Block "
                          "(time DATETIME, newblock SMALLINT UNSIGNED, "
                          "ip VARCHAR(15), port SMALLINT UNSIGNED)")
                db.commit()
                c.execute("INSERT INTO Block (time, newblock, ip, port) VALUES "
                          "(%s,%s,%s,%s)", (timenow, newfoundblock, ip, port))
                db.commit()

            summodule = 0
            maxtemp = 0
            i = 0
            for devData in data['Devs']:
                sumdevmodule = 0

                deviceid = int(devData['ID'])
                devStatData = data['Stats'][i]

                try:
                    sumdevmodule0 = modNumDict['{0},{1}'.format(minerid,
                                                                deviceid)]
                except:
                    sumdevmodule0 = 0
                j = 0
                sumlw = 0
                for key in devStatData:
                    if key[0:10] == 'Local work':
                        lw = int(devStatData[key])
                        sumlw += lw
                        j += 1
                avglw = float(sumlw) / j
                for key in devStatData:
                    if key[-10:] == 'MM Version':
                        sumdevmodule += 1
                        moduleid = int(key[2:-11])
                        temp1 = int(devStatData['Temperature{0}'.
                                                format(moduleid * 2 - 1)])
                        temp2 = int(devStatData['Temperature{0}'.
                                                format(moduleid * 2)])
                        fan1 = int(devStatData['Fan{0}'.
                                               format(moduleid * 2 - 1)])
                        fan2 = int(devStatData['Fan{0}'.format(moduleid * 2)])
                        lw = int(devStatData['Local works{0}'.format(moduleid)])
                        dh = float(devStatData['Device hardware error{0}%'
                                               .format(moduleid)])
                        volt = int(devStatData['Voltage{0}'.format(moduleid)])
                        freq = int(devStatData['Frequency{0}'.format(moduleid)])

                        if temp1 != 255 and temp1 > maxtemp:
                            maxtemp = temp1
                        if temp2 != 255 and temp2 > maxtemp:
                            maxtemp = temp2

                        flag = [False for k in range(8)]

                        if temp1 == 255 or temp2 == 255:
                            flag[0] = True
                        if temp1 > 80 or temp2 > 80:
                            flag[1] = True
                        if temp1 < 40 or temp2 < 40:
                            flag[2] = True
                        if dh > 5.0:
                            flag[3] = True
                        if volt != volt0:
                            flag[4] = True
                        if time0 is not None:
                            c.execute("SELECT localwork FROM Module_{0} WHERE "
                                      "ip=%s AND port=%s AND deviceid=%s AND "
                                      "moduleid=%s".format(time0),
                                      (ip, port, deviceid, moduleid))
                            result = c.fetchall()
                            if result:
                                lw0 = result[0][0]
                            else:
                                lw0 = -1
                        else:
                            lw0 = -1
                        if lw == lw0:
                            flag[5] = True
                        if lw < avglw * 0.8:
                            flag[6] = True
                        if fan1 + fan2 == 0:
                            flag[7] = True

                        param = (ip, port, deviceid, moduleid, temp1, temp2,
                                 fan1, fan2, lw, dh, volt, freq)
                        moduleParam.append(param)
                        error = False
                        for f in flag:
                            error = error or f
                        if error:
                            param = (ip, port, deviceid, moduleid, False,
                                     False, False) + tuple(flag)
                            errorParam.append(param)

                deviceParam.append((ip, port, deviceid,
                                    sumdevmodule, sumdevmodule0))
                summodule += sumdevmodule
                if sumdevmodule < sumdevmodule0:
                    errorParam.append(
                        (ip, port, deviceid, 0, False, False,
                         sumdevmodule0 - sumdevmodule, False,
                         False, False, False, False, False, False, False)
                    )
                i += 1

            for poolData in data['Pools']:
                poolid = poolData['POOL']
                alive = True if poolData['Status'] == 'Alive' else False
                url = poolData['URL']
                lst = datetime.fromtimestamp(int(poolData['Last Share Time']))
                lst = '{:%Y_%m_%d_%H_%M}'.format(lst)
                poolParam.append((ip, port, poolid, alive, url, lst))

            minerParam = (ip, port, True, sumdevice, sumdevice0, summodule,
                          summodule0, elapsed, megahash, block, newblock,
                          newfoundblock, rate1hr, rate15min, maxtemp)
        c.execute(command[0], minerParam)
        if deviceParam:
            c.executemany(command[1], deviceParam)
        if moduleParam:
            c.executemany(command[2], moduleParam)
        if poolParam:
            c.executemany(command[3], poolParam)
        if errorParam:
            c.executemany(command[4], errorParam)
        db.commit()
        dataQueue.task_done()
    c.close()
    db.close()


def analyze(dataQueue, timenow, cfg):

    threadNum = int(cfg['Database']['threadnum'])
    user = cfg['Database']['user']
    passwd = cfg['Database']['passwd']
    dbname = cfg['Database']['dbname']

    db = MySQLdb.connect(host="localhost", user=user, passwd=passwd, db=dbname)
    c = db.cursor()
    c.execute("SHOW TABLES LIKE 'Miner\_%'")
    tables0 = c.fetchall()
    if not tables0:
        time0 = None
    else:
        time0 = tables0[-1][0][6:]

    # avoid a python bug: http://bugs.python.org/issue7980
    datetime.strptime("2014_01_01_00_00", '%Y_%m_%d_%H_%M')
    c.execute("CREATE TABLE Miner_{0} "
              "(ip VARCHAR(15), "
              "port SMALLINT UNSIGNED, "
              "alive BOOL, "
              "sumdevice TINYINT UNSIGNED, "
              "sumdevice0 TINYINT UNSIGNED, "
              "summodule TINYINT UNSIGNED, "
              "summodule0 TINYINT UNSIGNED, "
              "elapsed INT, "
              "megahash FLOAT, "
              "block SMALLINT UNSIGNED, "
              "newblock SMALLINT UNSIGNED, "
              "newfoundblock SMALLINT UNSIGNED, "
              "rate1hr FLOAT, "
              "rate15min FLOAT, "
              "maxtemperature TINYINT UNSIGNED)".format(timenow))
    db.commit()
    c.execute("CREATE TABLE Device_{0} "
              "(ip VARCHAR(15), "
              "port SMALLINT UNSIGNED, "
              "deviceid TINYINT UNSIGNED, "
              "summodule TINYINT UNSIGNED, "
              "summodule0 TINYINT UNSIGNED)".format(timenow))
    db.commit()
    c.execute("CREATE TABLE Module_{0} "
              "(ip VARCHAR(15), "
              "port SMALLINT UNSIGNED, "
              "deviceid TINYINT UNSIGNED, "
              "moduleid TINYINT UNSIGNED, "
              "temperature1 TINYINT UNSIGNED, "
              "temperature2 TINYINT UNSIGNED, "
              "fan1 SMALLINT UNSIGNED, "
              "fan2 SMALLINT UNSIGNED, "
              "localwork INT UNSIGNED, "
              "hwerror FLOAT, "
              "voltage SMALLINT UNSIGNED, "
              "frequency SMALLINT UNSIGNED)".format(timenow))
    db.commit()
    c.execute("CREATE TABLE Pool_{0} "
              "(ip VARCHAR(15), "
              "port SMALLINT UNSIGNED, "
              "poolid TINYINT UNSIGNED, "
              "alive BOOL, "
              "url VARCHAR(64), "
              "lastsharetime DATETIME)".format(timenow))
    db.commit()
    c.execute("CREATE TABLE Error_{0} "
              "(ip VARCHAR(15), "
              "port SMALLINT UNSIGNED, "
              "deviceid TINYINT UNSIGNED, "
              "moduleid TINYINT UNSIGNED, "
              "connectionfailed BOOL, "
              "missingdevice BOOL, "
              "missingmodule BOOL, "
              "temperature255 BOOL, "
              "temperature80 Bool, "
              "temperature40 Bool, "
              "hwerrorhigh Bool, "
              "wrongvoltage BOOL, "
              "localworkstop BOOL, "
              "localworklow BOOL, "
              "fanstop BOOL)".format(timenow))
    db.commit()
    lock = threading.Lock()
    for i in range(threadNum):
        t = threading.Thread(target=dbThread,
                             args=(dataQueue, user, passwd, dbname, timenow,
                                   time0, int(cfg['Cgminer']['voltage']),
                                   cfg['devNumDict'], cfg['modNumDict'], lock))
        t.daemon = True
        t.start()
    dataQueue.join()

    c.execute("CREATE TABLE IF NOT EXISTS Aliverate (time DATETIME, "
              "modrate FLOAT, alivemod INT UNSIGNED, totalmod INT UNSIGNED, "
              "iprate FLOAT, aliveip INT UNSIGNED, totalip INT UNSIGNED)")
    db.commit()
    c.execute("SELECT COUNT(DISTINCT ip) FROM Miner_{0} "
              "WHERE alive=true".format(timenow))
    aliveip = c.fetchall()[0][0]
    c.execute("SELECT COUNT(DISTINCT ip), SUM(summodule), SUM(summodule0) "
              "FROM Miner_{0}".format(timenow))
    (totalip, alivemod, totalmod) = c.fetchall()[0]
    modrate = float(alivemod) / float(totalmod)
    iprate = float(aliveip) / float(totalip)
    c.execute("INSERT INTO Aliverate (time, modrate, alivemod, totalmod, "
              "iprate, aliveip, totalip) VALUES(%s,%s,%s,%s,%s,%s,%s)",
              (timenow, modrate, alivemod, totalmod, iprate, aliveip, totalip))
    db.commit()
    c.close()
    db.close()
