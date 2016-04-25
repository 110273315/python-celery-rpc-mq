#!/bin/bash
# by 

dois=$1
if [ -z $dois ]; then
        echo " please... (start/stop/restart) ! " 
        exit 0
fi

startjob()
{
python addJob.py & >/dev/null 2>&1
python addreward.py & >/dev/null 2>&1
python addsendmail.py & >/dev/null 2>&1
python addsendmsg.py & >/dev/null 2>&1
python addsendsms.py & >/dev/null 2>&1
python addtask.py & >/dev/null 2>&1
python custsync.py & >/dev/null 2>&1
python custinfosync.py & >/dev/null 2>&1
python doreward.py & >/dev/null 2>&1
python dosendmail.py & >/dev/null 2>&1
python dosendmsg.py & >/dev/null 2>&1
python dosendsms.py & >/dev/null 2>&1
python findJob.py & >/dev/null 2>&1
python preparereward.py & >/dev/null 2>&1
python preparesendmail.py & >/dev/null 2>&1
python preparesendmsg.py & >/dev/null 2>&1
python preparesendsms.py & >/dev/null 2>&1
python sessionclose.py & >/dev/null 2>&1
python addsendapp.py & >/dev/null 2>&1
python preparesendapp.py & >/dev/null 2>&1
python dosendapp.py & >/dev/null 2>&1
python tagsync.py & >/dev/null 2>&1
python tasks.py & >/dev/null 2>&1
python usercheck.py & >/dev/null 2>&1
python disabletagtask.py & >/dev/null 2>&1
python runtask.py & >/dev/null 2>&1
python updatetagname.py & >/dev/null 2>&1
exit 0
}

if [ $dois = start ]; then
        startjob

elif [ $dois = stop ]; then
        pkill -9 python
        rm -f sche-*

elif [ $dois = restart ]; then
        pkill -9 python
        rm -f shce-*
        startjob
fi
