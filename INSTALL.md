Requirement
-----------
```
sudo apt-get install apache2 mysql-server mysql-client \
libapache2-mod-wsgi-py3 python3 python3-pip
sudo pip3 install Flask mysql-python-connector-rf
```

MySQL
-----
* login with root.

    ```
    mysql -u root -p
    ```
* add new user `ams` and new database `ams`.

    ```
    create database ams;
    grant all privileges on ams.* to ams@'%' identified by "PASSWD";
    grant FILE on *.* to ams@localhost;
    ```

Configuration
-------------
* modify AMS config file `/etc/ams.conf`
* copy Apache2 config file

    ```
    sudo cp config/000-default.conf /etc/apache2/sites-available/000-default.conf
    sudo service apache2 restart
    ```
* load crontab file

    ```
    crontab config/cron.tab
    ```
