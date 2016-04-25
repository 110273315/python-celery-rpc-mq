#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from celery import Celery,platforms
from kombu import Exchange, Queue
from config import *
import mysql.connector
import json
import uuid
import datetime
import time

ONCE_CAPACITY = 5000

app = Celery("srjob.job", broker=amqp_url)


platforms.C_FORCE_ROOT = True

app.conf.update(
    CELERY_TRACK_STARTED=True,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_IMPORTS = ("addsendapp","preparesendapp","dosendapp","addJob","addreward","addsendmail","addsendmsg","addsendsms","addtask","custinfosync","custsync","doreward","dosendmail","dosendmsg","dosendsms","preparereward","preparesendmail","preparesendmsg","preparesendsms","sessionclose","tagsync","tasks","usercheck",),
    CELERYBEAT_SCHEDULE={
		'find-job-every-1-minutes': {
            'task': 'srjob.job.find',
            'schedule': datetime.timedelta(seconds=60),
        }
    }
)

diff_time = time.timezone
def utc_now():
    return datetime.datetime.now() + datetime.timedelta(seconds=diff_time)



@app.task(name="srjob.job.find")
def findJob():
    redisdb = ensure_redis()

    listlen = redisdb.llen("job")
    for i in range(0, listlen):
        listid = redisdb.lindex("job",i)
        task = redisdb.hgetall(listid)
        if task['isenable'] == '1':
            task_id = task['_id']
            oldtime = task['nexttime'].encode('utf-8')
            taskargu = eval(task['arguments'])
            tasktypecode = taskargu['tasktypecode']
            if datetime.datetime.strptime(oldtime, "%Y-%m-%d %H:%M:%S") < (datetime.datetime.now() + datetime.timedelta(seconds=1)):
                #当tasktypecode为1时，启动打标签job
                if tasktypecode == 1:
                    app.send_task('srjob.usertag.addtag',args=[task],queue='addtask')
                if tasktypecode == 4:
                    app.send_task('srjob.custinfo.custsync',args=[],queue='custsync')
                if tasktypecode == 5:
                    print("5555555555555555555555555555")
                    app.send_task('srjob.session.multicustsessionclose',args=[])
                if taskargu['periodcode'] == 1:
                    nexttime = datetime.datetime.now() + datetime.timedelta(minutes=taskargu['minute'])
                if taskargu['periodcode'] == 2:
                    nexttime = datetime.datetime.now() + datetime.timedelta(hours=taskargu['hour'])
                    nexttime = nexttime + datetime.timedelta(minutes=taskargu['minute'])
                if taskargu['periodcode'] == 3:
                    #nexttime = datetime.datetime.now() + datetime.timedelta(days=1)
                    ptime = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d") + " " + taskargu['time']
                    ptime = datetime.datetime.strptime(ptime, "%Y-%m-%d %H:%M:%S")
                    if ptime <= datetime.datetime.now():
                        nexttime = datetime.datetime.now() + datetime.timedelta(days=1)
                        nexttime = datetime.datetime.strftime(nexttime, "%Y-%m-%d") + " " + taskargu['time']
                        nexttime = datetime.datetime.strptime(nexttime, "%Y-%m-%d %H:%M:%S")
                    else:
                        nexttime = ptime
                if taskargu['periodcode'] == 4:
                    y = datetime.datetime.strftime(datetime.datetime.now(),'%Y')
                    mon = datetime.datetime.strftime(datetime.datetime.now(),'%m')
                    if (int(mon)+1) in [1,3,5,7,8,10,12]:
                        d = 31
                    elif (int(mon)+1) == 2:
                        if ((int(y) % 100 == 0 and int(y) % 400 == 0) or (int(y) % 100 != 0 and int(y) % 4 == 0)):
                            d = 29
                        else:
                            d = 28
                    elif (int(mon)+1) == 13:
                        d = 31
                    else:
                        d = 30
                    ptime = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d") + " " + taskargu['time']
                    ptime = datetime.datetime.strptime(ptime, "%Y-%m-%d %H:%M:%S")
                    if ptime <= datetime.datetime.now():
                        nexttime = datetime.datetime.now() + datetime.timedelta(days=d)
                        nexttime = datetime.datetime.strftime(nexttime, "%Y-%m-%d") + " " + taskargu['time']
                        nexttime = datetime.datetime.strptime(nexttime, "%Y-%m-%d %H:%M:%S")
                    else:
                        nexttime = ptime
                    #nexttime = datetime.datetime.now() + datetime.timedelta(days=d)
                    #nexttime = datetime.datetime.strftime(nexttime, "%Y-%m-%d") + " " + taskargu['time']
                    #nexttime = datetime.datetime.strptime(nexttime, "%Y-%m-%d %H:%M:%S")
                if taskargu['periodcode'] == 5:
                    ptime = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d") + " " + taskargu['time']
                    ptime = datetime.datetime.strptime(ptime, "%Y-%m-%d %H:%M:%S")
                    if ptime <= datetime.datetime.now():
                        nexttime = datetime.datetime.now() + datetime.timedelta(days=7)
                        nexttime = datetime.datetime.strftime(nexttime, "%Y-%m-%d") + " " + taskargu['time']
                        nexttime = datetime.datetime.strptime(nexttime, "%Y-%m-%d %H:%M:%S")
                    else:
                        nexttime = ptime
                    #nexttime = datetime.datetime.now() + datetime.timedelta(days=7)
                    #nexttime = datetime.datetime.strftime(nexttime, "%Y-%m-%d") + " " + taskargu['time']
                    #nexttime = datetime.datetime.strptime(nexttime, "%Y-%m-%d %H:%M:%S")
                redisdb.hset(listid,"nexttime",datetime.datetime.strftime(nexttime, "%Y-%m-%d %H:%M:%S"))
def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv
def _decode_list(data):
     rv = []
     for item in data:
         if isinstance(item, unicode):
             item = item.encode('utf-8')
         elif isinstance(item, list):
             item = _decode_list(item)
         elif isinstance(item, dict):
             item = _decode_dict(item)
         rv.append(item)
     return rv
if __name__ == "__main__":
    # 使用sys.argv参数运行
    # app.worker_main()

    # 使用自定义参数运行
    # --beat同时开启beat模式，即运行按计划发送task的实例
    # 应确保全局只有一份同样的beat
    app.worker_main(["worker", "--beat", "--loglevel=debug","-n","jobfind.%h","-s","./sche-jobfind"])
