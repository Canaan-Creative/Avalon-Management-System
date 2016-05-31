Build
-----
* Install required packages:

	```
	apt-get install simple-cdd
	```

* Create `private.conf`:

	Special characters in root and ams password should be backslash-escaped.

	MySQL root password should only contain alphabets and numbers.

* Copy customed `ams.conf` to `extras/root/etc/`

* Build:

	```
	./build
	```
