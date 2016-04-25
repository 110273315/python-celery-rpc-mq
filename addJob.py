#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from config import *
from celery import Celery,platforms
from kombu import Exchange, Queue
import mysql.connector
import json
import uuid
import datetime
import time
import sys

reload(sys)

sys.setdefaultencoding('utf8')


ONCE_CAPACITY = 5000

app = Celery("srjob.job", broker=amqp_url)


platforms.C_FORCE_ROOT = True

app.conf.update(
    CELERY_TRACK_STARTED=True,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_IMPORTS = ("addreward","addsendmail","addsendmsg","addsendsms","addtask","custinfosync","custsync","doreward","dosendmail","dosendmsg","dosendsms","findJob","preparereward","preparesendmail","preparesendmsg","preparesendsms","sessionclose","tagsync","tasks","usercheck","addsendapp","preparesendapp","dosendapp",)
)

diff_time = time.timezone
def utc_now():
    return datetime.datetime.now() + datetime.timedelta(seconds=diff_time)



#添加定时任务
@app.task(name="srjob.job.add")
def addJob(task):
    redisdb = ensure_redis()
    mydb = connect()
    ensure_mysql()

    task = json.loads(task)

    tagid = int(task["tagid"])
    task_id = 0
    if "taskid" in task.keys():
        task_id = task["taskid"]
    if "isenabled" in task.keys():
        isenable = task["isenabled"]
    if "periodcode" in task.keys():
        periodcode = task["periodcode"]
    if "minte" in task.keys():
        minte = task["minute"]
    if "hour" in task.keys():
        hous = task["hour"]
    if "time" in task.keys():
        timess = task["time"]
    if "month" in task.keys():
        months = task["month"]
    if "week" in task.keys():
        week = task["week"]
    if "taskname" in task.keys():
        taskname = task["taskname"]
    customer = task["customer"]

    filtercondition = json.dumps(customer,ensure_ascii=False)
    print(filtercondition)
    if "tasktypecode" in task.keys():
        tasktypecode = task["tasktypecode"]
    if "createrid" in task.keys():
        createrid = task["createrid"]
    if "modifierid" in task.keys():
        modifierid = task["modifierid"]

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
    cursor = mydb.cursor()
    filtercondition = str(filtercondition).replace("'",'"')
    if task_id != 0:
        updatesql = ("UPDATE sr_sys_schedule_task set taskname=\"%s\",filtercondition=\'%s\',tasktypecode=%d,periodcode=%d,starttime=\"%s\",nexttime=\"%s\",modifierid=\"%s\",modifiedtime=NOW() where id = %d" % (taskname,filtercondition,tasktypecode,periodcode,starttime,nexttime,modifierid,task_id))
        print(updatesql)
        cursor.execute(updatesql)
        mydb.commit()
        redisdb.hmset("job:"+str(task_id),{"arguments": _decode_dict(task), "isenable": isenable,"nexttime":nexttime})
    else:
        sql = ("INSERT INTO sr_sys_schedule_task(id,taskname,tasksource,filtercondition,tasktypecode,periodcode,starttime,nexttime,runninglevel,isenabled,createrid,createdtime,modifierid,modifiedtime) values (null,\"%s\",%d,\'%s\',%d,%d,\"%s\",\"%s\",2,1,\"%s\",NOW(),null,null)" % (taskname,tagid,filtercondition,tasktypecode,periodcode,starttime,nexttime,createrid))
        print(sql)
        #保存到mysql
        cursor.execute(sql)
        task_id = cursor.lastrowid
        mydb.commit()
        print("task_id="+str(task_id))
        redisdb.hmset("job:"+str(task_id),{
            "_id": task_id,
            "task": "srjob.job.add",
            "taskname": taskname,
            "arguments": _decode_dict(task),
            "isenable":isenable,
            "nexttime":nexttime,
            "begin_time": datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'),
            "status": "WAITTED"
        })
        redisdb.lpush("job","job:"+str(task_id))

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
    app.worker_main(["worker", "--loglevel=debug","-n","addJob.%h"])
