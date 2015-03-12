Local Hashrate
--------------

.. code-block:: sql

    SELECT a.time,
           b.time previous_time,
           SUM(IF(
               a.precise_time > b.precise_time
                   AND a.precise_time - b.precise_time > a.elapsed - b.elapsed -1 
                   AND a.precise_time - b.precise_time < a.elapsed - b.elapsed +1,
               (a.total_mh - b.total_mh) / (a.elapsed - b.elapsed), a.total_mh / a.elapsed
           )) mhs
      FROM miner a 
      JOIN miner b 
        ON a.ip = b.ip AND a.port = b.port AND a.time > b.time
      LEFT OUTER JOIN miner c 
        ON a.ip = c.ip AND a.port = c.port AND a.time > c.time AND b.time < c.time
     WHERE c.time IS NULL
     GROUP BY a.time;

Installation
------------

.. code-block:: bash

    apt-get install python3 python3-yaml
    wget http://ftp.ntu.edu.tw/MySQL/Downloads/Connector-Python/mysql-connector-python-1.2.3.tar.gz
    tar zxpfv mysql-connector-python-1.2.3.tar.gz
    cd mysql-connector-python-1.2.3
    python3 setup.py install
