#!/usr/bin/env python2

import json
import urllib
import urllib2
import hashlib
import hmac
import time
import sys

import MySQLdb


def getjs(poolcfg, url):
    i = 0
    while i < int(poolcfg['retry']):
        try:
            nonce = '{:.0f}'.format(time.time()*1000)
            signature = hmac.new(poolcfg['api_secret_key'], msg=nonce +
                                 poolcfg['username'] + poolcfg['api_key'],
                                 digestmod=hashlib.sha256).hexdigest().upper()
            post_content = {'key': poolcfg['api_key'],
                            'signature': signature,
                            'nonce': nonce}
            param = urllib.urlencode(post_content)
            request = urllib2.Request(url, param,
                                      {'User-agent': 'bot-cex.io-' +
                                       poolcfg['username']})
            js = urllib2.urlopen(request).read()
            return json.loads(js)
        except Exception, e:
            print str(e),
            sys.stdout.flush()
            time.sleep(1)
            i += 1
    return None


def ghash(pool):
    url2 = 'https://cex.io/api/ghash.io/workers'
    try:
        proxy_handler = urllib2.ProxyHandler({})
        opener = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener)

        dict2 = getjs(pool, url2)
        if dict2 is None:
            hs2 = None
        else:
            try:
                hs2 = float(dict2[pool['username'] + '.' +
                                  pool['workername']]['last1h'])
            except KeyError:
                hs2 = None
        return hs2
    except:
        return None


def ozco(pool):
    url = 'http://ozco.in/api.php?api_key=' + pool['api_key']
    try:
        js = urllib2.urlopen(url).read()
        dict0 = json.loads(js)
        hs2 = ''.join(dict0['worker'][pool['username'] + '.' +
                                      pool['workername']]['current_speed']
                      .split(','))
        return float(hs2)
    except:
        return None


def btcchina(pool):
    url = 'https://pool.btcchina.com/api?api_key=' + pool['api_key']
    try:
        js = urllib2.urlopen(url).read()
        dict0 = json.loads(js)
        fullname = '{}.{}'.format(pool['username'], pool['workername'])
        for worker in dict0['user']['workers']:
            if worker['worker_name'] == fullname:
                hs2 = worker['hashrate']
        return float(hs2) / 1000000.0
    except:
        return None


def ckproxy(pool):
    try:
        url = 'http://solo.ckpool.org/ahusers/' + pool['api_key']
        js = urllib2.urlopen(url).read()
        dict0 = json.loads(js)
        hs2 = dict0['hashrate1hr']
        if hs2[-1] == 'P':
            hs2 = float(hs2[:-1]) * 1000000000
        elif hs2[-1] == 'T':
            hs2 = float(hs2[:-1]) * 1000000
        elif hs2[-1] == 'G':
            hs2 = float(hs2[:-1]) * 1000
        else:
            hs2 = float(hs2[:-1])
        return hs2
    except:
        return '0'


def poolrate(timenow, cfg):
    rate = []
    for pool in cfg['poolList']:
        if pool['name'] == 'ghash':
            rate.append(ghash(pool))
        elif pool['name'] == 'ozco':
            rate.append(ozco(pool))
        elif pool['name'] == 'ckproxy':
            rate.append(ckproxy(pool))
        elif pool['name'] == 'btcchina':
            rate.append(btcchina(pool))
        else:
            rate.append(0.0)

    user = cfg['Database']['user']
    passwd = cfg['Database']['passwd']
    dbname = cfg['Database']['dbname']

    db = MySQLdb.connect(host="localhost", user=user, passwd=passwd, db=dbname)
    c = db.cursor()

    try:
        c.execute("SELECT SUM(rate1hr) as sum from Miner_{0}".format(timenow))
        table = c.fetchall()
        local = table[0][0]
    except:
        local = None

    command1 = "INSERT INTO Hashrate (time, local"
    command2 = ") VALUES (%s, %s"
    param = [timenow, local]

    c.execute("SHOW TABLES LIKE 'Hashrate'")
    if not c.fetchall():
        command = ("CREATE TABLE IF NOT EXISTS Hashrate "
                   "(time DATETIME, local FLOAT")
        for pool in cfg['poolList']:
            command += ", `{0}` FLOAT".format(pool['label'])
        command += ")"

        c.execute(command)
        db.commit()
        i = 0
        for pool in cfg['poolList']:
            command1 += ', `{0}`'.format(pool['label'])
            command2 += ', %s'
            param.append(rate[i])
            i += 1
    else:
        c.execute("DESCRIBE Hashrate")
        labelTable = c.fetchall()
        labels = []
        for lt in labelTable:
            labels.append(lt[0])
        i = 0
        for pool in cfg['poolList']:
            if not pool['label'] in labels:
                c.execute("ALTER TABLE Hashrate ADD `{0}` "
                          "FLOAT".format(pool['label']))
                db.commit()
            command1 += ', `{0}`'.format(pool['label'])
            command2 += ', %s'
            param.append(rate[i])
            i += 1

    command = command1 + command2 + ')'
    c.execute(command, tuple(param))
    db.commit()
    c.close()
    db.close()
