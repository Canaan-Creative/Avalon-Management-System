AMS - Avalon Management System
==============================
A toolset to manage BTC Farm

Installation
------------

##### Requirements
As root
```
apt-get install apache2 mysql-server mysql-client \
libapache2-mod-wsgi-py3 python3 python3-pip redis-server
pip3 install Flask setuptools python-jose redis
pip3 install --egg mysql-connector-python-rf
```

##### MySQL Setup
* Login with root:

    ```
    mysql -u root -p
    ```
* Add new user `ams` and new database `ams`:

    ```
    CREATE database ams;
    GRANT ALL PRIVILEGES ON ams.* TO ams@'%' IDENTIFIED BY "PASSWD";
    GRANT FILE ON *.* TO ams@localhost;
	FLUSH PRIVILEGES;
    ```

  **_Note: replace PASSWD with the real password._**

##### Install from tar.gz
* Download the tar.gz files of ams-server and ams-client from [releases]( https://github.com/Canaan-Creative/Avalon-Management-System/releases).
* Install server:

    ```
    tar xzpvf ams-server-VERSION.tar.gz
    cd ams-server-VERSION
    sudo python3 setup.py install
    ```
* Install client:

    ```
    tar zxpvf ams-client-VERSION.tar.gz
    sudo mkdir /var/www/html/ams
    sudo cp -r ams-client/* /var/www/html/ams/
    ```

  **_Note: replace VERSION with the real version number._**

##### Configuration
* Modify AMS config file `/etc/ams.conf`.
* ```git clone https://github.com/Canaan-Creative/Avalon-Management-System.git ams-git```
* Copy Apache2 config file:

    ```
    sudo cp ams-git/config/000-default.conf /etc/apache2/sites-available/000-default.conf
    sudo service apache2 restart
    ```
* Load crontab file:

    ```
    crontab ams-git/config/cron.tab
    ```



Build (for Developer)
---------------------
* server:

    ```
    cd server
    python3 setup.py sdist
    ```

* client:

    Requirement:

    ```
    sudo apt-get install npm
    sudo ln -s /usr/bin/nodejs /usr/bin/node
    sudo npm install -g grunt-cli jshint

    ```

    Build:

    ```
    cd client
    npm install
    grunt prereq
    grunt build
    ```

Structure
---------
Database: /usr/local/lib/python3.5/dist-packages/ams/
Config file: /etc/ams.conf
Tools: /usr/local/bin/amscli
Frontend: /var/www/html/ams

Known Issues
------------
####Apache Error: 'assert tlock is not None'

* Reason:

    mod_wsgi version is too low (<= 3.4).

* Solution:

    As root
    ```
    pip3 install mod_wsgi
    rm /usr/lib/apache2/modules/mod_wsgi.so
    ln -s /usr/local/lib/python3.4/dist-packages/mod_wsgi/server/mod_wsgi-py34.cpython-34m.so /usr/lib/apache2/modules/mod_wsgi.so
    service apache2 restart
    ```
    **_NOTE: the version number in_** `python3.4` **_and_** `mod_wsgi-py34.cpython-34m.so` **_may vary._**

####MySQL5.7: Create table failed with invalid date
* Reason:

    http://dev.mysql.com/doc/refman/5.7/en/sql-mode.html#sql-mode-setting

* Sloution:

    mysql -u root -ppassword -e "SET GLOBAL sql_mode = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,ALLOW_INVALID_DATES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';"
