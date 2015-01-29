#!/usr/bin/env python2

from __future__ import print_function
import os
import datetime
import sys
import threading
import Queue
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()

import matplotlib
matplotlib.use('Agg', warn=False)
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import numpy as np
import matplotlib.cm as cm
from matplotlib import gridspec
import MySQLdb


def heatmapThread(user, passwd, dbname, now_s, miner_queue, result_queue, lock):

    db = MySQLdb.connect(host="localhost", user=user, passwd=passwd, db=dbname)
    c = db.cursor()
    while True:
        try:
            (ip, zone, column, row) = miner_queue.get(False)
        except Queue.Empty:
            break
        c.execute("SELECT SUM(summodule), SUM(summodule0), "
                  "SUM(rate15min), MAX(maxtemperature) FROM "
                  "Miner_{0} WHERE IP='{1}'".format(now_s, ip))
        result = c.fetchall()
        try:
            module_num = '{0}/{1}'.format(result[0][0], result[0][1])
        except:
            item = {'ip': ip, 'zone': zone, 'row': row, 'column': column,
                    'maxtemp': None}
            result_queue.put(item)
            miner_queue.task_done()
            continue

        rate15min = int(result[0][2])
        if len(str(rate15min)) < 3:
            rate = "{0} MH/s".format(rate15min)
        elif len(str(rate15min)) < 6:
            rate = ("{0:." + str(6 - len(str(rate15min))) +
                    "f} GH/s").format(rate15min / 1000.0)
        elif len(str(rate15min)) < 9:
            rate = ("{0:." + str(9 - len(str(rate15min))) +
                    "f} TH/s").format(rate15min / 1000000.0)
        else:
            rate = ("{0:." + str(12 - len(str(rate15min))) +
                    "f} PH/s").format(rate15min / 1000000000.0)
        max_temperature = result[0][3]
        c.execute("SELECT temp FROM Module_{0} "
                  "WHERE IP='{1}'".format(now_s, ip))
        result = c.fetchall()

        tmp = 0
        n = 0
        for r in result:
            if r[0] > 0 and r[0] < 255:
                tmp += r[0]
                n += 1
        try:
            avg_temperature = float(tmp) / n
        except:
            avg_temperature = 0
        temperature = '{0:.1f}/{1}'.format(avg_temperature, max_temperature)
        if max_temperature == 0:
            max_temperature = 256
        item = {'ip': ip, 'zone': zone, 'row': row, 'column': column,
                'rate': rate,
                'temp': temperature,
                'modnum': module_num,
                'maxtemp': max_temperature}
        result_queue.put(item)
        miner_queue.task_done()


def heatmap(now, cfg):

    now_s = '{:%Y_%m_%d_%H_%M}'.format(now)
    filename = "hm-{}.png".format(now_s)
    print("Plotting into " +
          os.path.join(cfg['Folder']['hashrategraph'], filename) + " ... ",
          end="")
    sys.stdout.flush()

    miner_queue = Queue.Queue()
    result_queue = Queue.Queue()
    z = 0
    for zone in cfg['farm']['zone']:
        row_num = zone['layers']
        i = 0
        for miner in zone['miner']:
            column = i / row_num
            row = row_num - 1 - i % row_num
            try:
                miner_queue.put((miner['ip'], z, column, row))
            except:
                result_queue.put({'ip': 'skip', 'zone': z,
                                  'row': row, 'column': column})
            i += 1
        z += 1

    threadNum = int(cfg['Database']['threadnum'])
    user = cfg['Database']['user']
    passwd = cfg['Database']['passwd']
    dbname = cfg['Database']['dbname']

    db = MySQLdb.connect(host="localhost", user=user, passwd=passwd, db=dbname)
    c = db.cursor()

    c.execute("SHOW TABLES LIKE 'Miner\_%'")
    result = c.fetchall()
    for row in result:
        if datetime.datetime.strptime(row[0][6:], '%Y_%m_%d_%H_%M') <= now:
            tmp = row[0]
    now_s = tmp[6:]

    c.close()
    db.close()
    lock = threading.Lock()
    for i in range(threadNum):
        t = threading.Thread(target=heatmapThread,
                             args=(user, passwd, dbname, now_s,
                                   miner_queue, result_queue, lock))
        t.daemon = True
        t.start()
    miner_queue.join()

    T = []
    text = []
    skip = []
    err = []
    while True:
        try:
            item = result_queue.get(False)
        except Queue.Empty:
            break
        zone = item['zone']
        row = item['row']
        column = item['column']
        while len(T) < zone + 1:
            T.append([])
            text.append([])
            err.append([])
            skip.append([])
        while len(T[zone]) < row + 1:
            T[zone].append([])
            text[zone].append([])
        while len(T[zone][row]) < column + 1:
            T[zone][row].append([])
            text[zone][row].append([])
        if item['ip'] != 'skip' and item['maxtemp'] is not None:
            T[zone][row][column] = item['maxtemp']
            text[zone][row][column] = item
        elif item['ip'] == 'skip':
            while len(skip) < zone + 1:
                skip.append([])
            T[zone][row][column] = 256
            skip[zone].append((column, row))
            text[zone][row][column] = item
        else:
            while len(err) < zone + 1:
                err.append([])
            T[zone][row][column] = 256
            err[zone].append((column, row))
            text[zone][row][column] = item

    for z in range(len(T)):
        T[z] = np.ma.masked_greater(T[z], 254.5)
    cmap = cm.jet
    norm = matplotlib.colors.Normalize(vmin=40, vmax=50)
    scal = cm.ScalarMappable(norm=norm, cmap=cmap)

    fig = plt.figure(figsize=(float(cfg['Heatmap']['width']
                                    )/float(cfg['Heatmap']['dpi']),
                              float(cfg['Heatmap']['height']
                                    )/float(cfg['Heatmap']['dpi'])),
                     dpi=int(cfg['Heatmap']['dpi']), facecolor="white")
    titlefont = {'family': cfg['Heatmap']['font_family1'],
                 'weight': 'normal',
                 'size': int(cfg['Heatmap']['font_size1'])}
    labelfont = {'family': cfg['Heatmap']['font_family2'],
                 'weight': 'normal',
                 'size': int(cfg['Heatmap']['font_size2'])}
    ticks_font = matplotlib.font_manager.FontProperties(
        family=cfg['Heatmap']['font_family3'], style='normal',
        size=int(cfg['Heatmap']['font_size3']), weight='normal',
        stretch='normal')

    plot_num = 0
    hr = []
    z = 0
    for zone in cfg['farm']['zone']:
        subplot_num = (len(T[z][0]) + zone['plot_split'] -
                       1) / zone['plot_split']
        for i in range(0, subplot_num):
            hr.append(zone['layers'])
        plot_num += subplot_num
        z += 1
    gs = gridspec.GridSpec(plot_num, 2, width_ratios=[97, 3], height_ratios=hr)

    kk = 0
    ss = 0
    for z in range(0, len(T)):
        zone = cfg['farm']['zone'][z]
        jj = 0
        for k in range((len(T[z][0]) + zone['plot_split'] - 1) /
                       zone['plot_split']):
            ax = plt.subplot(gs[k + kk, 0])
            if k == 0 and z == 0:
                # only the first plotted has title
                ax.set_title(cfg['Heatmap']['title'], fontdict=titlefont)
            gci = ax.pcolormesh(T[z], cmap=cmap, norm=norm,
                                edgecolors='white', linewidths=0)
            for p in err[z]:
                ax.add_patch(matplotlib.patches.Rectangle((p[0], p[1]), 1, 1,
                                                          facecolor='none',
                                                          edgecolor='r',
                                                          hatch='/'))
            for p in skip[z]:
                ax.add_patch(matplotlib.patches.Rectangle((p[0], p[1]), 1, 1,
                                                          facecolor='none'))
            for i in range(len(T[z])):
                for j in range(jj, jj + zone['plot_split']):
                    if j >= len(T[z][i]):
                        break

                    if text[z][i][j]['ip'] == 'skip':
                        continue
                    text_x = text[z][i][j]['column'] + .5
                    text_y = text[z][i][j]['row'] + .5
                    if text[z][i][j]['maxtemp'] is None:
                        ax.text(text_x, text_y, 'N/A', ha='center', va='center',
                                fontproperties=ticks_font, color='k')
                        continue

                    ax.text(text_x, text_y + .25, text[z][i][j]['modnum'],
                            ha='center', va='center', fontproperties=ticks_font,
                            color='k')
                    ax.text(text_x, text_y, text[z][i][j]['rate'],
                            ha='center', va='center', fontproperties=ticks_font,
                            color='k')
                    ax.text(text_x, text_y - .25, text[z][i][j]['temp'],
                            ha='center', va='center', fontproperties=ticks_font,
                            color='k')

            # single zone may have multi subplots
            # split according to cfg['Zone#'][plot_split]
            # method: alway plot the full fig in one subplot**,
            #         use x/ylim to cut print area out.
            # so no need to change xticks or xticklabels
            #     ** texts(mod_num,speed) not included, which must be writen
            #     according to subplot shelves, referring to the upper if-else.
            ax.set_xticks(np.linspace(0.5, len(T[z][0]) - 0.5, len(T[z][0])))
            xl = []
            for a in range(1 + ss, len(T[z][0]) + 1 + ss):
                xl.append(str(a))
            yl = []
            for a in range(1, len(T[z]) + 1):
                yl.append(str(a))

            ax.set_xticklabels(tuple(xl))

            ax.set_yticks(np.linspace(0.5, len(T[z]) - 0.5, len(T[z])))
            ax.set_yticklabels(tuple(yl))

            for label in ax.get_xticklabels():
                label.set_fontproperties(ticks_font)
            for label in ax.get_yticklabels():
                label.set_fontproperties(ticks_font)

            ax.set_ylabel("Layers", fontdict=labelfont)
            ax.tick_params(tick1On=False, tick2On=False)

            ax.set_xlim(jj / zone['plot_split'] * zone['plot_split'],
                        (jj / zone['plot_split'] + 1) * zone['plot_split'])
            ax.set_ylim(0, zone['layers'])
            jj += zone['plot_split']

        ss += len(T[z][0])
        kk += k + 1

    # only the last plotted have x-axis label
    ax.set_xlabel("Shelves", fontdict=labelfont)

    # color bar
    ax = plt.subplot(gs[0:, 1])
    cbar = plt.colorbar(gci, cax=ax)
    cbar.set_label('Temperature ($^{\circ}C$)', fontdict=labelfont)
    cbar.set_ticks(np.linspace(40, 50, 6))
    cbar.set_ticklabels(('40', '42', '44', '46', '48', '50'))
    for tick in cbar.ax.yaxis.majorTicks:
        tick.label2.set_fontproperties(ticks_font)

    plt.tight_layout()

    plt.savefig(os.path.join(cfg['Folder']['heatmap'], filename))
    plt.clf()
    print("Done.")
    return filename


def hashrate(now, cfg):

    user = cfg['Database']['user']
    passwd = cfg['Database']['passwd']
    dbname = cfg['Database']['dbname']

    db = MySQLdb.connect(host="localhost", user=user, passwd=passwd, db=dbname)
    c = db.cursor()

    c.execute("DESCRIBE Hashrate")
    result = c.fetchall()
    labels = []
    for row in result:
        if row[0] == 'time':
            continue
        labels.append(row[0])
    vs = [[] for i in range(len(labels))]
    t = []

    c.execute("SELECT * FROM Hashrate WHERE time "
              "BETWEEN %s AND %s ORDER BY time",
              ((now - datetime.timedelta(seconds=25 * 3600)).isoformat(),
               now.isoformat()))
    result = c.fetchall()
    c.close()
    db.close()
    for row in result:
        t.append((row[0] - now).total_seconds())
        for i in range(len(vs)):
            vs[i].append(row[i + 1])

    if len(t) < 2:
        print("More log files are needed for plotting.")
        return None
    filename = "hr-{:%Y_%m_%d_%H_%M}.png".format(now)
    print("Plotting into " +
          os.path.join(cfg['Folder']['hashrategraph'], filename) +
          " ... ", end="")
    sys.stdout.flush()

    for k in range(0, len(t)):
        t[k] = t[k] / 3600.0

    x = np.array(t)
    ys = []
    fs = []
    for v in vs:
        y = np.array(v)
        ys.append(y)
        fs.append(interp1d(x, y))
    ymax = np.amax(np.hstack(ys))
    xnew = np.linspace(t[0], t[-1], 1800)

    fig = plt.figure(
        figsize=(
            float(cfg['Hashrate']['width']) / float(cfg['Hashrate']['dpi']),
            float(cfg['Hashrate']['height']) / float(cfg['Hashrate']['dpi'])),
        dpi=int(cfg['Hashrate']['dpi']),
        facecolor="white"
    )
    titlefont = {'family': cfg['Hashrate']['font_family1'],
                 'weight': 'normal',
                 'size': int(cfg['Hashrate']['font_size1'])}
    ticks_font = matplotlib.font_manager.FontProperties(
        family=cfg['Hashrate']['font_family2'], style='normal',
        size=int(cfg['Hashrate']['font_size2']), weight='normal',
        stretch='normal')

    colorlist = ['b-', 'c-', 'g-', 'r-', 'y-', 'm-']
    plots = []
    for i in range(0, len(vs)):
        p, = plt.plot(xnew, fs[i](xnew), colorlist[i])
        plots.append(p)
        plt.legend(plots, labels, loc=2, prop=ticks_font)

    # x axis tick label
    xticklabel = []
    xmax = now - datetime.timedelta(
        seconds=(now.hour - (now.hour / 2) * 2) * 3600 + now.minute * 60)
    xmin = xmax
    xticklabel.append(xmin.strftime("%H:%M"))
    for i in range(0, 12):
        xmin = xmin - datetime.timedelta(seconds=7200)
        xticklabel.append(xmin.strftime("%H:%M"))
    xticklabel = xticklabel[::-1]

    # y axis tick label
    ymax_s = str(int(ymax))
    flag = int(ymax_s[0])
    yticklabel = ['0']
    if flag == 1:
        # 0.1;0.2;0.3....
        ystep = 1 * (10 ** (len(ymax_s) - 2))
        ylim = int(ymax + ystep - 1) / ystep * ystep
        for i in range(1, int(ylim / ystep)):
            yticklabel.append("{:,}".format(i * (10 ** (len(ymax_s) - 2))))
    elif flag >= 2 and flag <= 3:
        # 0.2;0.4;0.6...
        ystep = 2 * (10 ** (len(ymax_s) - 2))
        ylim = int(ymax + ystep - 1) / ystep * ystep
        for i in range(1, int(ylim / ystep)):
            yticklabel.append("{:,}".format(i * 2 * (10 ** (len(ymax_s) - 2))))
    elif flag >= 4 and flag <= 6:
        # 0.25;0.50;0.75...
        ystep = 25*(10**(len(ymax_s)-3))
        ylim = int(ymax + ystep - 1) / ystep * ystep
        for i in range(1, int(ylim / ystep)):
            yticklabel.append("{:,}".format(i * 25 * (10 ** (len(ymax_s) - 3))))
    else:
        # 0.5;1.0;1.5...
        ystep = 5 * (10 ** (len(ymax_s) - 2))
        ylim = int(ymax + ystep - 1) / ystep * ystep
        for i in range(1, int(ylim / ystep)):
            yticklabel.append("{:,}".format(i * 5 * (10 ** (len(ymax_s) - 2))))

    ax = plt.gca()
    ax.set_xticks(np.linspace((xmin - now).total_seconds() / 3600.0,
                              (xmax - now).total_seconds() / 3600.0, 13))
    ax.set_xticklabels(tuple(xticklabel))
    ax.set_yticks(np.linspace(0, ylim - ystep, len(yticklabel)))
    ax.set_yticklabels(tuple(yticklabel))

    ax.tick_params(tick1On=False, tick2On=False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.set_title(cfg['Hashrate']['title'], fontdict=titlefont)

    for label in ax.get_xticklabels():
        label.set_fontproperties(ticks_font)
    for label in ax.get_yticklabels():
        label.set_fontproperties(ticks_font)

    plt.axis([-24, 0, 0, ylim])

    plt.grid(color='0.75', linestyle='-')
    plt.tight_layout()

    plt.savefig(os.path.join(cfg['Folder']['hashrategraph'], filename))
    print("Done.")
    plt.clf()
    return filename
