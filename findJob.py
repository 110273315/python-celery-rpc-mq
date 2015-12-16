#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from celery import Celery,platforms
from kombu import Exchange, Queue
import pymongo
import mysql.connector
import json
import uuid
import datetime
import time

ONCE_CAPACITY = 5000

amqp_url = "amqp://guest:guest@172.16.0.64/"
mongo_url = "mongodb://172.16.0.64/srjob"
mysql_conf = {
    'host': '172.16.0.176',
    'port': 3306,
    'database': 'smartrewardsdev_30',
    'user': 'srdev',
    'password': 'sr_dev1124'
}

mongo = None
def ensure_mongo():
    global mongo
    if mongo:
        return mongo

    mongo = pymongo.MongoClient(mongo_url);
    mongo = mongo[mongo_url.split("/")[-1]]
    return mongo


mydb = None
def ensure_mysql():
    global mydb
    if mydb:
        return mydb

    mydb = mysql.connector.connect(**mysql_conf);
    return mydb


app = Celery("srjob.job", broker=amqp_url)


platforms.C_FORCE_ROOT = True

app.conf.update(
    CELERY_TRACK_STARTED=True,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_IMPORTS = ("addtask","addJob","tasks","usercheck","tagsync",),
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
    ensure_mongo()
    ensure_mysql()

    tasks = mongo["job"].find({"isenable": 1})


    for task in tasks:
        task_id = task['_id']
        oldtime = task['nexttime'].encode('utf-8')
        tasktypecode = task['arguments']['tasktypecode']
        if datetime.datetime.strptime(oldtime, "%Y-%m-%d %H:%M:%S") < (datetime.datetime.now() + datetime.timedelta(seconds=60)):
            #当tasktypecode为1时，启动打标签job
            if tasktypecode == 1:
                print(_decode_dict(task['arguments']))
                app.send_task('srjob.usertag.add',args=[_decode_dict(task['arguments'])],queue='addtask')
            if tasktypecode == 4:
                app.send_task('srjob.custinfo.custsync',args=[],queue='custsync')
            if task['arguments']['periodcode'] == 1:
                nexttime = datetime.datetime.now() + datetime.timedelta(minutes=task['arguments']['minute'])
            if task['arguments']['periodcode'] == 2:
                nexttime = datetime.datetime.now() + datetime.timedelta(hours=task['arguments']['hour'])
                nexttime = nexttime + datetime.timedelta(minutes=task['arguments']['minute'])
            if task['arguments']['periodcode'] == 3:
                nexttime = datetime.datetime.strftime((datetime.datetime.now() + datetime.timedelta(days=1)), "%Y-%m-%d %H:%M:%S")
            if task['arguments']['periodcode'] == 4:
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
                nexttime = datetime.datetime.strftime((datetime.datetime.now() + datetime.timedelta(days=d)), "%Y-%m-%d %H:%M:%S")
            if task['arguments']['periodcode'] == 5:
                nexttime = datetime.datetime.strftime((datetime.datetime.now() + datetime.timedelta(days=7)), "%Y-%m-%d %H:%M:%S")
            mongo["job"].update_one({"_id":task_id},
                                 {"$set":{"nexttime":datetime.datetime.strftime(nexttime, "%Y-%m-%d %H:%M:%S")}})
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
if __name__ == "__main__":
    # 使用sys.argv参数运行
    # app.worker_main()

    # 使用自定义参数运行
    # --beat同时开启beat模式，即运行按计划发送task的实例
    # 应确保全局只有一份同样的beat
    app.worker_main(["worker", "--beat", "--loglevel=debug","--concurrency=10","-n","jobfind.%h"])
