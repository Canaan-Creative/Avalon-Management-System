#!/usr/bin/env python3

import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib.request
import json


def numberShorten(number):
    prefix = [
        {'prefix': ' E', 'base': 1000000000000},
        {'prefix': ' P', 'base': 1000000000},
        {'prefix': ' T', 'base': 1000000},
        {'prefix': ' G', 'base': 1000},
        {'prefix': ' M', 'base': 1}
    ]
    for p in prefix:
        if (number >= p['base']):
            if number >= p['base'] * 100:
                return '{}{}'.format(round(number / p['base'], 1), p['prefix'])
            elif number >= p['base'] * 10:
                return '{}{}'.format(round(number / p['base'], 2), p['prefix'])
            else:
                return '{}{}'.format(round(number / p['base'], 3), p['prefix'])
    return number


def getBalance(address):
    url = ("https://blockchain.info/address/{}?"
           "format=json&limit=0").format(address)
    try:
        response = urllib.request.urlopen(url, timeout=10)
        result = json.loads(response.read().decode())
        return result['final_balance'] / 1.0e8
    except:
        return 'Connection Failed'


def sendReport(cfg):

    mail = cfg['Email']
    farm = cfg['Farm']

    # Get Shortlog:
    response = urllib.request.urlopen('http://127.0.0.1/api/shortlog')
    shortlog = json.loads(response.read().decode())['result']

    time = datetime.datetime.fromtimestamp(shortlog['time'])
    hashrate = numberShorten(shortlog['hashrate'])

    # Get Pool Summary
    response = urllib.request.urlopen('http://127.0.0.1/api/pool_summary/latest')
    pool_summary = json.loads(response.read().decode())['result']

    # Get Balance
    balance = getBalance(farm['balance'])

    user = mail['from_address'].split('@')[0]

    me = "{}<{}>".format(user, mail['from_address'])
    to_list = mail['to_list'].split(';')

    msg = MIMEMultipart('alternative')
    msg['Subject'] = (
        "[AMS Report][{}][{:%y%m%d%H}]"
        "[{:.1f} BTC][{}][IP{}][MOD{}]").format(
            farm['code'],
            time,
            balance,
            hashrate,
            shortlog['node_num'],
            shortlog['module_num']
        )
    msg['From'] = me
    msg['To'] = mail['to_list']
    if 'cc' in mail:
        msg['CC'] = mail['cc']
        to_list.extend(mail['cc'].split(';'))
    if 'bcc' in mail:
        to_list.extend(mail['bcc'].split(';'))

    content = """\
<html>
    <head></head>
    <body>
        <h3>AMS Report</h3>
        <p>Time: {0:%Y-%m-%d %H:%M}</p>
        <p>Server: {1}</p>
        <p>Hashrate: {2}</p>
        <p>Node Number: {3}</p>
        <p>Module Number: {4}</p>
        <p>Balance: {5} BTC</p>
        <p>Info: <a href="{6}">{6}</a></p>
        <table style="border-collapse: collapse; border: 1px solid black;">
            <thead>
                <tr>
                    <th style="border: 1px solid black;">Pool</th>
                    <th style="border: 1px solid black;">User</th>
                    <th style="border: 1px solid black;">Hs</th>
                    <th style="border: 1px solid black;">Node Number</th>
                    <th style="border: 1px solid black;">Module Number</th>
                <tr>
            </thead>
            <tbody>
                $tbody$
            </tbody>
        </table>
    </body>
</html>
""".format(
        time,
        farm['name'],
        hashrate,
        shortlog['node_num'],
        shortlog['module_num'],
        balance,
        farm['info'],
    )
    tbody = ''
    for pool in pool_summary:
        pool['ghs'] = numberShorten(pool['ghs'] * 1.0e3)
        tbody += """\
                <tr>
                    <td style="border: 1px solid black;">{url}</td>
                    <td style="border: 1px solid black;">{username}</td>
                    <td style="border: 1px solid black;">{ghs}</td>
                    <td style="border: 1px solid black;">{node_num:.0f}</td>
                    <td style="border: 1px solid black;">{module_num:.0f}</td>
                </tr>\n""".format(**pool)
    mail['content'] = content.replace('$tbody$', tbody)

    msg_html = MIMEText(mail['content'], 'HTML')
    msg.attach(msg_html)

    s = smtplib.SMTP()
    s.connect(mail['smtp_server'])
    s.login(user, mail['password'])
    s.sendmail(me, to_list, msg.as_string())
    s.close()
