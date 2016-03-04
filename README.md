AMS - Avalon Management System
==============================
A toolset to manage BTC Farm

Installation
------------

##### Requirements
As root
```
apt-get install apache2 mysql-server mysql-client \
libapache2-mod-wsgi-py3 python3 python3-pip
pip3 install Flask mysql-python-connector-rf setuptools
```

##### MySQL Setup
* Login with root:

    ```
    mysql -u root -p
    ```
* Add new user `ams` and new database `ams`:

    ```
    create database ams;
    grant all privileges on ams.* to ams@'%' identified by "PASSWD";
    grant FILE on *.* to ams@localhost;
    ```

**_Note: replace PASSWD with the real password._**

##### Install from tar.gz
* Download the tar.gz files of ams-server and ams-client.
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
* Copy Apache2 config file:

    ```
    sudo cp config/000-default.conf /etc/apache2/sites-available/000-default.conf
    sudo service apache2 restart
    ```
* Load crontab file:

    ```
    crontab config/cron.tab
    ```



Build
-----
* server:

    ```
    cd server
    python3 setup.py sdist
    ```

* client:

    ```
    cd client
    sudo npm install -g grunt-cli jshint
    npm install
    grunt prereq
    grunt build
    ```
