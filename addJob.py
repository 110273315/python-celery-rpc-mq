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
    CELERY_IMPORTS = ("findJob","tagsync","usercheck","tasks","addtask",)
)

diff_time = time.timezone
def utc_now():
    return datetime.datetime.now() + datetime.timedelta(seconds=diff_time)



#添加定时任务
@app.task(name="srjob.job.add")
def addJob(task):
    ensure_mongo()
    ensure_mysql()

    task = json.loads(task)
    print(task)
    tagid = int(task["tagid"])

    isenable = task["isenabled"]
    periodcode = task["periodcode"]
    minte = task["minute"]
    hous = task["hour"]
    timess = task["time"]
    months = task["month"]
    week = task["week"]
    taskname = task["taskname"]
    filtercondition = _decode_dict(task["customer"])
    tasktypecode = task["tasktypecode"]
    createrid = task["createdid"]

    #当按分钟运行
    if periodcode == 1:
        nexttime = datetime.datetime.now() + datetime.timedelta(minutes=minte)
        nexttime = datetime.datetime.strftime(nexttime, "%Y-%m-%d %H:%M:%S")
        starttime = minte
    #当按小时运行
    if periodcode == 2:
        nexttime = datetime.datetime.now() + datetime.timedelta(hours=hous)
        nexttime = nexttime + datetime.timedelta(minutes=minte)
        nexttime = datetime.datetime.strftime(nexttime, "%Y-%m-%d %H:%M:%S")
        starttime = str(hous)+":"+str(minte)
    #当按天运行 保存每天运行的时间
    if periodcode == 3:
        t1 = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d') + ' ' + timess
        if datetime.datetime.strptime(t1, "%Y-%m-%d %H:%M:%S") < datetime.datetime.now():
            nexttime = datetime.datetime.strftime((datetime.datetime.now() + datetime.timedelta(days=1)), "%Y-%m-%d %H:%M:%S")
        else :
            nexttime = datetime.datetime.strftime(datetime.datetime.strptime(t1, "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
        starttime = timess
    #当按月运行 
    if periodcode == 4:
        starttime = str(months) + ',' + timess
        m = datetime.datetime.strftime(datetime.datetime.now(),'%m')
        d = datetime.datetime.strftime(datetime.datetime.now(),'%d')
        #当当前日期大于传入的日期
        if int(d) > int(months):
            if int(m) == 12:
                y = int(datetime.datetime.strftime(datetime.datetime.now(),'%Y'))+int('1');
                m = "01"
            else:
                y = datetime.datetime.strftime(datetime.datetime.now(),'%Y')
                m = int(m)+1
                if m < 10:
                    m = '0' + str(m)
            nexttime = str(y) + '-' + str(m) + '-' + str(months) + ' ' + timess
        else :
            #当当前日期等于传入的日期
            if int(d) == int(months):
                t2 = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d') + ' ' + timess
                if datetime.datetime.strptime(t2, "%Y-%m-%d %H:%M:%S") > datetime.datetime.now():
                    nexttime = datetime.datetime.strftime(datetime.datetime.strptime(t2, "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
                else:
                    if int(m) == 12:
                        y = int(datetime.datetime.strftime(datetime.datetime.now(),'%Y'))+1
                        m = "01"
                    else:
                        y = datetime.datetime.strftime(datetime.datetime.now(),'%Y')
                        m = int(m)+1
                        if m < 10:
                            m = '0' + str(m)
                    nexttime = str(y) + '-' + str(m) + '-' + str(months) + ' ' + timess
            #当当前日期小于传入的日期
            else:
                y = datetime.datetime.strftime(datetime.datetime.now(),'%Y')
                nexttime = str(y) + '-' + str(m) + '-' + str(months) + ' ' + timess
    #当按周运行
    if periodcode == 5:
        starttime = str(week) + ',' + timess
        w = datetime.datetime.now().weekday()
        #w = datetime.datetime.strptime("2015-12-07", "%Y-%m-%d").weekday()
        #当当前星期几大于传入的星期几
        if w > week:
            nexttime = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=(7-(w-int(week)))), '%Y-%m-%d') + ' ' + timess
        else:
            if w < week:
                nexttime = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=(int(week)-w)), '%Y-%m-%d') + ' ' + timess
            else :
                t3 = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d') + ' ' + timess
                if datetime.datetime.strptime(t3, "%Y-%m-%d %H:%M:%S") > datetime.datetime.now():
                    nexttime = datetime.datetime.strftime(datetime.datetime.strptime(t3, "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
                else:
                    nexttime = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=7), '%Y-%m-%d') + ' ' + timess
    #task['nexttime'] = datetime.datetime.strptime(nexttime, '%Y-%m-%d %H:%M:%S')
    task['nexttime'] = nexttime
    task['starttime'] = starttime
    print(datetime.datetime.strptime(nexttime, '%Y-%m-%d %H:%M:%S'))    

    sql = ("INSERT INTO sr_sys_schedule_task(id,taskname,tasksource,filtercondition,tasktypecode,periodcode,starttime,nexttime,runninglevel,isenabled,createrid,createdtime,modifierid,modifiedtime) values (null,\"%s\",%d,\"%s\",%d,%d,\"%s\",\"%s\",2,1,\"%s\",NOW(),null,null)" % (taskname,tagid,filtercondition,tasktypecode,periodcode,starttime,nexttime,createrid))
    #保存到mysql
    cursor = mydb.cursor()
    cursor.execute(sql)
    task_id = cursor.lastrowid
    mydb.commit()
    print("task_id="+str(task_id))
    # 保存job
    mongo["job"].insert({
        "_id": task_id,
        "task": "srjob.job.add",
        "arguments": task,
        "isenable":isenable,
        "nexttime":nexttime,
        "begin_time": utc_now(),
        "status": "WAITTED"
    })

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
    app.worker_main(["worker", "--loglevel=debug","--concurrency=10","-n","addJob.%h"])
