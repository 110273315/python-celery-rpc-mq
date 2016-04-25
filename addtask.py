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

app = Celery("srjob.usertag", broker=amqp_url)


platforms.C_FORCE_ROOT = True

app.conf.update(
    CELERY_TRACK_STARTED=True,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_IMPORTS = ("addsendapp","preparesendapp","dosendapp","addJob","addreward","addsendmail","addsendmsg","addsendsms","custinfosync","custsync","doreward","dosendmail","dosendmsg","dosendsms","findJob","preparereward","preparesendmail","preparesendmsg","preparesendsms","sessionclose","tagsync","tasks","usercheck",)
)

diff_time = time.timezone
def utc_now():
    return datetime.datetime.now() + datetime.timedelta(seconds=diff_time)


@app.task(queue="addtask")
def addtag(task):
    redisdb = ensure_redis()
    mydb = connect()
    ensure_mysql()

    task = _decode_dict(task)
    #task = eval(str(task))

    jobid = task['_id']
    task = eval(task['arguments'])
    print(task);
    tagid = task["tagid"]
    orgid = task["orgid"]
    #task_id = task["taskid"]
    customer = task["customer"]
    inserttask = ("INSERT INTO sr_tag_task(id,orgid,historytype,historysource,tagid,isusetagsql,custlist,tagsql,isactivities,createrid,createdtime) values (null,\"%s\",2,1,\"%s\",1,NULL,\"%s\",0,NULL,NOW());" % (orgid,tagid,_decode_dict(customer)))
    #保存到mysql
    cursor = mydb.cursor()
    cursor.execute(inserttask)
    task_id = cursor.lastrowid
    mydb.commit()

    # 保存task状态
    # taskmeta的数据不可定制，所以来份自己的
    redisdb.hmset("task:"+str(task_id),{
        "_id": task_id,
        "task": "srjob.usertag.add",
        "arguments": _decode_dict(task),
        "begin_time": utc_now(),
        "isenable": 1,
        "prepare": 0,
        "status": "STARTED"
    })
    redisdb.lpush("task","task:"+str(task_id))
    try:
        logsql = ("insert into sr_sys_schedule_log (taskid,taskname,exectime,statecode) VALUES (%d,\"%s\",NOW(),1)" % (int(jobid),task["taskname"]))
        cursor.execute(logsql)
        logid = cursor.lastrowid
        mydb.commit()
        # 查询sql语句
        sql = "SELECT sc.id FROM sr_cust_customer sc "
        conditions = []
        conditions.append("WHERE sc.statuscode='1'")
        if "mobile" in customer.keys():
            conditions.append(" AND sc.mobile = \"%s\"" % customer["mobile"])
        if "shopid" in customer.keys():
            conditions.append(" AND sc.orgid = \"%s\"" % customer["shopid"])
        if "gendercode" in customer.keys():
            conditions.append(" AND sc.gendercode = %d" % int(str(customer["gendercode"]).encode('utf-8')))
        if "typecode" in customer.keys():
            conditions.append(" AND sc.id in (SELECT custid from sr_cust_type where typecode = %d and isdelete = 0)" % int(str(customer["typecode"]).encode('utf-8')))
        if "sourcecode" in customer.keys():
            conditions.append(" AND sc.channelcode = %d" % int(str(customer["sourcecode"]).encode('utf-8')))
        if "frequencymin" in customer.keys():
            conditions.append(" AND sc.tradetimes >= %d" % int(str(customer["frequencymin"]).encode('utf-8')))
        if "frequencymax" in customer.keys():
            conditions.append(" AND sc.tradetimes <= %d" % int(str(customer["frequencymax"]).encode('utf-8')))
        if "startamount" in customer.keys():
            conditions.append(" AND sc.totaltradeamount >= %d" % int(str(customer["startamount"]).encode('utf-8')))
        if "endamount" in customer.keys():
            conditions.append(" AND sc.totaltradeamount <= %d" % int(str(customer["endamount"]).encode('utf-8')))
        if "tags" in customer.keys():
            if customer["tags"] != "":
                conditions.append(" AND sc.id in (select custid from sr_tag_cust stc where stc.tagid IN (\"%s\"))" % customer["tags"])
        if "agemin" in customer.keys():
            conditions.append(" AND sc.birthday<=DATE_SUB(now(),INTERVAL %d YEAR)" % int(str(customer["agemin"]).encode('utf-8')))
        if "agemax" in customer.keys():
            conditions.append(" AND sc.birthday>=DATE_SUB(now(),INTERVAL %d YEAR)" % int(str(customer["agemax"]).encode('utf-8')))
        if "createdstarttime" in customer.keys():
            conditions.append(" AND sc.createdtime >= \"%s 00:00:00\"" % customer["createdstarttime"])
        if "createdendtime" in customer.keys():
            conditions.append(" AND sc.createdtime <= \"%s 23:59:59\"" % customer["createdendtime"])
        if "tradestartdate" in customer.keys():
            conditions.append(" AND sc.id in (select custid from sr_cust_trade st where st.tradetime >= \"%s 00:00:00\")" % customer["tradestartdate"])
        if "tradeenddate" in customer.keys():
            conditions.append(" AND sc.id in (select custid from sr_cust_trade st where st.tradetime <= \"%s 23:59:59\")" % customer["tradeenddate"])
        sql = sql + ''.join(conditions)
        print(sql)

        # 执行sql查询
        #cursor = mydb.cursor()
        cursor.execute(sql)

        # 创建子任务
        bulk = redisdb.pipeline()
        count = 0
        
        while True:
            row = cursor.fetchone()
            if not row:
                break            
            userid = row[0]            
            bulk.lpush("task_"+str(task_id),userid)            
            count += 1
            if count % ONCE_CAPACITY == 0:
                bulk.execute()
            
        if count % ONCE_CAPACITY:
            bulk.execute()

        # 倒计数
        # 一并加上查询到的数量
        redisdb.hmset("task:"+str(task_id),{"logid":logid,"queried": count, "downcount": count})
        #创建子任务
        #最后创建子任务，易于处理downcount
        #for x in range((count + ONCE_CAPACITY -1) /ONCE_CAPACITY):
        if count:
            app.send_task('srjob.usertag.usercheck',args=[task_id, userid, tagid,logid],queue='usercheck')
        else:
            updatelogsql = ("update sr_sys_schedule_log set statecode = 2 where id = %d" % int(logid))
            cursor.execute(updatelogsql)
            mydb.commit()
            redisdb.hmset("task:"+str(task_id),{"status":"SUCCESS", "end_time":utc_now()})
    except Exception as e:
        logsql = ("insert into sr_sys_schedule_log (taskid,taskname,exectime,statecode) VALUES (%d,\"%s\",NOW(),3)" % (int(jobid),task["taskname"]))
        cursor.execute(logsql)
        mydb.commit()
        # 更新task状态
        redisdb.hmset("task:"+str(task_id),{"status": "FAILURE", "error": str(e), "end_time": utc_now()})
        raise

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
    app.worker_main(["worker", "--loglevel=debug","-n","autoaddtask.%h","-Qaddtask"])
