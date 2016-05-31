#!/bin/bash
sleep 5
if [ -f /media/$1/interfaces ]
then
	cp /media/$1/interfaces /etc/network/interfaces
	service networking stop
	service networking start
	ip a | unix2dos > /media/$1/interfaces.done.txt
fi
