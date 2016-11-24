#!/usr/bin/env python3

import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib.request
import json
import ssl


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

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # Get Shortlog:
    res = urllib.request.urlopen('https://127.0.0.1/api/shortlog', context=ctx)
    shortlog = json.loads(res.read().decode())['result']

    time = datetime.datetime.fromtimestamp(shortlog['time'])
    hashrate = numberShorten(shortlog['hashrate'])

    # Get Pool Summary
    res = urllib.request.urlopen(
        'https://127.0.0.1/api/pool_summary/latest',
        context=ctx
    )
    pool_summary = json.loads(res.read().decode())['result']

    # Get Balance
    if 'balance' in farm:
        balance = getBalance(farm['balance'])
    else:
        balance = None

    user = mail['from_address'].split('@')[0]

    me = "{}<{}>".format(user, mail['from_address'])
    to_list = mail['to_list'].split(';')

    msg = MIMEMultipart('alternative')
    msg['Subject'] = (
        "[AMS Report][{}]"
        "{}[{}Hs][{} IP][{} MOD]").format(
            farm['code'],
            '[{:.1f} BTC]'.format(balance) if balance is not None else '',
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
        <h3>{0} ({1}) AMS Report {2:%Y-%m-%d %H:%M}</h3>
        <table style="border-collapse: collapse; border: 1px solid black;">
            <thead>
                <tr>
                    <th style="border: 1px solid black;">Pool</th>
                    <th style="border: 1px solid black;">User</th>
                    <th style="border: 1px solid black;">Hash/s</th>
                    <th style="border: 1px solid black;">Node Number</th>
                    <th style="border: 1px solid black;">Module Number</th>
                <tr>
            </thead>
            <tbody>
                $tbody$
            </tbody>
        </table>
        <p>Info: <a href="{3}">{3}</a></p>
    </body>
</html>
""".format(
        farm['name'],
        farm['mod'],
        time,
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
    tbody += """\
                <tr>
                    <td style="border: 1px solid black; font-weight: bold;"
                        colspan="2">Sum</td>
                    <td style="border: 1px solid black;">{}</td>
                    <td style="border: 1px solid black;">{:.0f}</td>
                    <td style="border: 1px solid black;">{:.0f}</td>
                </tr>\n""".format(
                    hashrate,
                    shortlog['node_num'],
                    shortlog['module_num'])
    mail['content'] = content.replace('$tbody$', tbody)

    msg_html = MIMEText(mail['content'], 'HTML')
    msg.attach(msg_html)

    s = smtplib.SMTP()
    s.connect(mail['smtp_server'])
    s.login(user, mail['password'])
    s.sendmail(me, to_list, msg.as_string())
    s.close()
