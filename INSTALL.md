Requirement
-----------
```
sudo apt-get install python python-django python-matplotlib python-mysqldb python-numpy python-paramiko mysql-server
```

MySQL Config
------------
* login with root.
    ```
    mysql -u root -p
    ```
* add new user `ams` and new database `ams_test`.

    ```
    create database ams_test;
    grant all privileges on ams_test.* to ams@localhost identified by "PASSWD";
    grant FILE on *.* to ams@localhost;
    ```

AMS Config
----------
* modify configuration files according to the examples in `etc/example`.
* change username and passwd in `www/status/login.php` line 11.
* change RPi ssh passwd in `www/status/restart_cgminer.py` line 11.
* copy everything in `www` folder to your www-server root path.
* change permission of `csv` folder.
    ```
    chmod 777 /path/to/ams/csv
    ```

Cron Config
-----------
```
crontab -e
```
```
       0     0-22/2   * *   *     cd /path/to/ams/bin/;./ams.py -m
15,30,45     0-22/2   * *   *     cd /path/to/ams/bin/;./ams.py
    */15     1-23/2   * *   *     cd /path/to/ams/bin/;./ams.py
       0          0   * *   *     cd /path/to/ams/bin/;./ams-dbclean.py
```
