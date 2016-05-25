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


def sendReport(mail):

    # Get Info:
    response = urllib.request.urlopen('http://127.0.0.1/api/shortlog')
    shortlog = json.loads(response.read().decode())['result']

    time = datetime.datetime.fromtimestamp(shortlog['time'])
    hashrate = numberShorten(shortlog['hashrate'])

    user = mail['from_address'].split('@')[0]

    me = "{}<{}>".format(user, mail['from_address'])
    to_list = mail['to_list'].split(';')

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "[AMS Report][{}][{:%y%m%d%H}][{}][IP{}][MOD{}]".format(
        mail['server_code'],
        time,
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

    mail['content'] = """\
<html>
    <head></head>
    <body>
        <h3>AMS Report</h3>
        <p>Time: {:%Y-%m-%d %H:%M}</p>
        <p>Server: {}</p>
        <p>Hashrate: {}</p>
        <p>Node Number: {}</p>
        <p>Module Number: {}</p>
    </body>
</html>
""".format(
        time,
        mail['server_code'],
        hashrate,
        shortlog['node_num'],
        shortlog['module_num']
    )
    msg_html = MIMEText(mail['content'], 'HTML')
    msg.attach(msg_html)

    s = smtplib.SMTP()
    s.connect(mail['smtp_server'])
    s.login(user, mail['password'])
    s.sendmail(me, to_list, msg.as_string())
    s.close()
