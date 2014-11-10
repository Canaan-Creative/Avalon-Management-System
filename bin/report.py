#!/usr/bin/env python2

from __future__ import print_function
import datetime
import smtplib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
import sys
import time

from django.template import loader, Context
from django.conf import settings
import MySQLdb


def post(mail, template_var):

    me = mail['user'] + "<" + mail['from_address'] + ">"
    msg = MIMEMultipart('related')
    msg['Subject'] = mail['subject']
    msg['From'] = me
    msg['To'] = mail['to_list']
    to_list = mail['to_list'].split(';')
    msg_alternative = MIMEMultipart('alternative')
    msg.attach(msg_alternative)

    if 'tmimg' in mail:
        tmimg = dict(path=mail['tmimg_dir'] + mail['tmimg'],
                     cid=str(uuid.uuid4()))

        with open(tmimg['path'], 'rb') as file:
            msg_tmimage = MIMEImage(file.read(),
                                    name=os.path.basename(tmimg['path']))
            msg.attach(msg_tmimage)
        template_var['tmimg_cid'] = tmimg['cid']
        msg_tmimage.add_header('Content-ID', '<{}>'.format(tmimg['cid']))
    if 'hsimg' in mail:
        hsimg = dict(path=mail['hsimg_dir'] + mail['hsimg'],
                     cid=str(uuid.uuid4()))

        with open(hsimg['path'], 'rb') as file:
            msg_hsimage = MIMEImage(file.read(),
                                    name=os.path.basename(hsimg['path']))
            msg.attach(msg_hsimage)
        template_var['hsimg_cid'] = hsimg['cid']
        msg_hsimage.add_header('Content-ID', '<{}>'.format(hsimg['cid']))
    tmp = mail['template'].split('/')
    template_dir = '/'.join(tmp[:-1])
    try:
        settings.configure(TEMPLATE_DIRS=(template_dir
                                          if template_dir else './',))
    except:
        pass
    t = loader.get_template(tmp[-1])
    c = Context(template_var)
    mail['content'] = t.render(c)
    msg_html = MIMEText(mail['content'], 'HTML')
    msg_alternative.attach(msg_html)

    for i in range(3):
        try:
            s = smtplib.SMTP()
            s.connect(mail['smtp_server'])
            s.login(mail['user'], mail['password'])
            s.sendmail(me, to_list, msg.as_string())
            s.close()
            return True
        except Exception, e:
            s.close()
            print(str(e), end="")
            sys.stdout.flush()
            time.sleep(10)
            continue
    return False


def sendMail(time_d, cfg):

    time = '{:%Y_%m_%d_%H_%M}'.format(time_d)

    # Attention: 'time' must be converted to the checkpoint time

    mail = cfg['Email']

    print("Sending Email to {}".format(mail['to_list']), end="... ")
    sys.stdout.flush()

    mail['user'] = mail['from_address'].split('@')[0]
    mail['hsimg_dir'] = cfg['Folder']['hashrategraph']
    mail['tmimg_dir'] = cfg['Folder']['heatmap']

    template_var = {}
    template_var['server_code'] = cfg['General']['server_code']
    template_var['time'] = '{:%Y.%m.%d %H:%M}'.format(time_d)

    if 'tmimg' in mail:
        template_var['tmimg'] = True
    if 'hsimg' in mail:
        template_var['hsimg'] = True
    if 'balance' in mail:
        template_var['balance'] = True
        template_var['balance_list'] = mail['balance']

    sum_balance = 0
    for balance in mail['balance']:
        sum_balance += float(balance['final_balance'])
    template_var['sum_balance'] = sum_balance

    user = cfg['Database']['user']
    passwd = cfg['Database']['passwd']
    dbname = cfg['Database']['dbname']

    db = MySQLdb.connect(host="localhost", user=user, passwd=passwd, db=dbname)
    c = db.cursor()

    # alive ip and mod
    c.execute("SELECT aliveip, totalip, alivemod, totalmod "
              "FROM Aliverate WHERE time=%s", (time,))
    table = c.fetchall()
    if table:
        template_var['active_ip_num'] = "{}/{}".format(*(table[-1][:2]))
        template_var['alive_mod_num'] = "{}/{}".format(*(table[-1][2:]))

    # block found in this period
    if cfg['General']['block_notify'] == 'true':
        if 'mail_period' in cfg['General']:
            time0_d = time_d - datetime.timedelta(
                seconds=int(cfg['General']['mail_period']))
            time0 = '{:%Y_%m_%d_%H_%M}'.format(time0_d)
            c.execute("SELECT * FROM Block WHERE time<=%s and time>%s",
                      (time, time0))
        else:
            c.execute("SELECT * FROM Block WHERE time=%s", (time, ))
        table = c.fetchall()
        if table:
            template_var['lucky'] = True
            template_var['lucky_list'] = []
            for t in table:
                template_var['lucky_list'].append({
                    'id':   '{}:{}'.format(*(t[2:])),
                    'num':  str(t[1])
                })
        else:
            template_var['lucky'] = False
    else:
        template_var['lucky'] = False

    c.execute("SELECT local FROM Hashrate WHERE time=%s", (time,))
    rate = int(c.fetchall()[0][0])
    if len(str(rate)) < 3:
        rate_s = "{0}MHs".format(rate)
    elif len(str(rate)) < 7:
        rate_s = ("{0:." + str(6 - len(str(rate))) + "f}GHs").format(
            rate / 1000.0)
    elif len(str(rate)) < 10:
        rate_s = ("{0:." + str(9 - len(str(rate))) + "f}THs").format(
            rate / 1000000.0)
    elif len(str(rate)) < 13:
        rate_s = ("{0:." + str(12 - len(str(rate))) + "f}PHs").format(
            rate / 1000000000.0)
    elif len(str(rate)) < 16:
        rate_s = ("{0:." + str(15 - len(str(rate))) + "f}EHs").format(
            rate / 1000000000000.0)
    else:
        rate_s = ("{0:0f}EHs").format(rate / 1000000000000.0)

    mail['subject'] = "[AMS Report][{}]{}[{:.0f}BTC][{}][IP{}][MOD{}]".format(
        template_var['server_code'],
        '[NEW BLOCK]' if template_var['lucky'] else '',
        template_var['sum_balance'],
        rate_s,
        template_var['active_ip_num'],
        template_var['alive_mod_num']
    )

    c.close()
    db.close()
    if post(mail, template_var):
        print(" Successed.")
    else:
        print(" Failed.")
