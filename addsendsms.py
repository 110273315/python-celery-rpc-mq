#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from celery import Celery,platforms
from kombu import Exchange, Queue
from celery import task
from config import *
import json
import uuid
import datetime
import time

ONCE_CAPACITY = 1

app = Celery("srjob.sendsms", broker=amqp_url)


platforms.C_FORCE_ROOT = True

app.conf.update(
    CELERY_TRACK_STARTED=True,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_IMPORTS = ("addsendapp","preparesendapp","dosendapp","addJob","addreward","addsendmail","addsendmsg","addtask","custinfosync","custsync","doreward","dosendmail","dosendmsg","dosendsms","findJob","preparereward","preparesendmail","preparesendmsg","preparesendsms","sessionclose","tagsync","tasks","usercheck",)
)

diff_time = time.timezone
def utc_now():
    return datetime.datetime.now() + datetime.timedelta(seconds=diff_time)

@app.task(name="srjob.sendsms.addsms")
def addsms(msg):
    redisdb = ensure_redis()

    task = json.loads(msg)
    if "esttime" in task.keys():
        esttime = task["esttime"]
    if "taskid" in task.keys():
        task_id = task["taskid"]
    if "campaignid" in task.keys():
        campaignid = task["campaignid"]

    redisdb.hmset("sendsms:"+str(task_id),{
        "_id": task_id,
        "task": "sendsms",
        "arguments": _decode_dict(task),
        "campaignid":campaignid,
        "esttime":esttime,
        "creat_time": utc_now(),
        "isenable":1,#1可用 0不可用
        "prepare":0,#1数据已准备 0数据未准备
        "status": "STARTED"
    })
    redisdb.rpush("sendsms","sendsms:"+str(task_id))

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
    app.worker_main(["worker","--loglevel=debug","-n","sendsms.%h"])