#!/usr/bin/env python2

import ConfigParser
import json


def configurate(configFile):
    config = ConfigParser.ConfigParser()
    config.read(configFile)
    configDict = dict(config._sections)
    for k in configDict:
        configDict[k] = dict(config._defaults, **configDict[k])
        configDict[k].pop('__name__', None)

    for key in configDict['Include']:
        if key == 'farm':
            continue
        subconfig = ConfigParser.ConfigParser()
        subconfig.read(configDict['Include'][key])
        subconfigDict = dict(subconfig._sections)
        for k in subconfigDict:
            subconfigDict[k] = dict(subconfig._defaults, **subconfigDict[k])
            subconfigDict[k].pop('__name__', None)
        for k in subconfigDict:
            if not k in configDict:
                configDict[k] = subconfigDict[k]
            else:
                for kk in subconfigDict[k]:
                    configDict[k][kk] = subconfigDict[k][kk]

    poolList = []
    for key in configDict:
        if key[:4] == 'Pool' and len(key) > 4:
            poolList.append(configDict[key])

    farmFile = configDict['Json']['farm']
    with open(farmFile, 'r') as farmF:
        farmStr = farmF.read()
        farmDict = json.loads(farmStr)
    configDict['farm'] = farmDict

    minerList = []
    modNumDict = {}
    devNumDict = {}
    for zone in farmDict['zone']:
        for miner in zone['miner']:
            if miner == 'skip':
                continue
            ip = miner['ip']
            for cgminer in miner['cgminer']:
                port = cgminer['port']
                minerID = '{0}:{1}'.format(ip, port)
                minerList.append(minerID)
                devNumDict[minerID] = len(cgminer['mod'])

                devID = 0
                summod = 0
                for mod in cgminer['mod']:
                    modNumDict['{0},{1}'.format(minerID, devID)] = mod
                    summod += mod
                    devID += 1
                modNumDict[minerID] = summod

    configDict['minerList'] = minerList
    configDict['modNumDict'] = modNumDict
    configDict['devNumDict'] = devNumDict
    configDict['poolList'] = poolList

    return configDict
