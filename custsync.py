#!/usr/bin/env python2.7
# coding:utf-8
from celery import Celery,platforms
from kombu import Exchange, Queue
from config import *
import mysql.connector
import json
import uuid
import datetime
import time
import pika
import uuid
import cf_wechat_pb2
import threading

app = Celery("srjob.custinfo", broker=amqp_url)

ONCENUM = 100
platforms.C_FORCE_ROOT = True

app.conf.update(
    CELERY_TRACK_STARTED=True,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_IMPORTS = ("addsendapp","preparesendapp","dosendapp","addJob","addreward","addsendmail","addsendmsg","addsendsms","addtask","custinfosync","doreward","dosendmail","dosendmsg","dosendsms","findJob","preparereward","preparesendmail","preparesendmsg","preparesendsms","sessionclose","tagsync","tasks","usercheck",)
)



@app.task(queue="custsync")
def custsync():
    #创建守护线程，处理amqp事件
    #程序会等待所有非守护线程结束，才会退出
    #守护线程在程序退出时，自动结束
    print("custsynccustsynccustsynccustsynccustsync")
    mydb = connect()
    ensure_mysql()
    rpc = ensure_rpc()
    redisdb = ensure_redis()
    cursor = mydb.cursor()
    logid = 0
    logsql = ("insert into sr_sys_schedule_log (taskid,taskname,exectime,statecode) VALUES (%d,\"%s\",NOW(),1)" % (26,"同步微信会员"))
    cursor.execute(logsql)
    logid = cursor.lastrowid
    mydb.commit()
    sql = "SELECT innerid,org_id FROM cf_account where method_code = 1 and enabled = 1"
    cursor = mydb.cursor()
    cursor.execute(sql)
    for row in cursor.fetchall(): 
        if not row:
            break
        account_id = row[0]
        org_id = row[1]

        req = cf_wechat_pb2.Message()
        req.header.sender="req_userinfo_sync"
        req.header.sender_type="type1"
        req.req_userinfo_sync.account_id = account_id
        print(req)
        data = req.SerializeToString()

        #第二个参数类型float，单位秒，缺省为None，不超时
        data = rpc.call(data,10)    #1 seconds timeout
        if data:
            reply = cf_wechat_pb2.Message()
            reply.ParseFromString(data)
            next_openid = reply.res_userinfo_sync.next_openid
            openidlist = reply.res_userinfo_sync.openid_list
            count = 0
            while True:
                print("openidlist=="+str(len(openidlist)))
                if count == 0:
                    count = count + 1
                    if len(openidlist) > 0:
                        temp = []
                        openids = ""
                        tempcount = 0
                        for i in range(len(openidlist)):
                            temp.append(openidlist[i])
                            openids=openids+openidlist[i].encode('utf-8')+","
                            if len(temp) == ONCENUM:
                                tempcount = tempcount + 1
                                openidlistid = str(uuid.uuid4())
                                redisdb.hmset("openidsync:"+openidlistid,{
                                    "_id": openidlistid,
                                    "openidlist": openids,
                                    "logid": logid,
                                    "lastid": 0,
                                    "account_id":account_id,
                                    "org_id":org_id
                                })

                                redisdb.lpush("openid","openidsync:"+openidlistid)
                                #app.send_task('srjob.custinfo.custinfosync',args=[temp],queue='custinfosync')
                                temp = []
                                openids = ""
                        if len(temp)>0:
                            openidlistid = str(uuid.uuid4())
                            redisdb.lpush("openid","openidsync:"+openidlistid)
                            redisdb.hmset("openidsync:"+openidlistid,{
                                "_id": openidlistid,
                                "openidlist": openids,
                                "logid": logid,
                                "lastid": 1,
                                "account_id":account_id,
                                "org_id":org_id
                            })
                            #app.send_task('srjob.custinfo.custinfosync',args=[temp],queue='custinfosync')
                    if len(openidlist) < 10000:
                        break
                else:
                    if len(openidlist) == 10000:
                        req = cf_wechat_pb2.Message()
                        req.header.sender="req_userinfo_sync"
                        req.header.sender_type="type1"
                        req.req_userinfo_sync.account_id = account_id
                        condition = req.req_userinfo_sync.customer_search_condition
                        condition.wechat_open_id=next_openid
                        data = req.SerializeToString()
                        data = rpc.call(data,60)    #1 seconds timeout
                        if data:
                            reply = cf_wechat_pb2.Message()
                            reply.ParseFromString(data)
                            next_openid = reply.res_userinfo_sync.next_openid
                            openidlist = reply.res_userinfo_sync.openid_list
                            if len(openidlist) != 0:
                                temps = []
                                openids = ""
                                #tempcount = 0
                                for i in range(len(openidlist)):
                                    temps.append(openidlist[i])
                                    openids=openids+openidlist[i].encode('utf-8')+","
                                    if len(temps) == ONCENUM:
                                        openidlistid = str(uuid.uuid4())
                                        print("len(temps)=="+str(len(temps)))
                                        redisdb.hmset("openidsync:"+openidlistid,{
                                            "_id": openidlistid,
                                            "openidlist": openids,
                                            "logid": logid,
                                            "lastid": 0,
                                            "account_id":account_id,
                                            "org_id":org_id
                                        })
                                        redisdb.lpush("openid","openidsync:"+openidlistid)
                                        temps=[]
                                        openids = ""
                            else:
                                redisdb.hmset("openidsync:"+openidlistid,{
                                    "_id": openidlistid,
                                    "openidlist": openids,
                                    "logid": logid,
                                    "lastid": 1,
                                    "account_id":account_id,
                                    "org_id":org_id
                                })
                                redisdb.lpush("openid","openidsync:"+openidlistid)

                        else:   #如果超时，返回None
                            if logid:
                                updatelogsql = ("update sr_sys_schedule_log set statecode = 3 where id = %d" % logid)
                                cursor = mydb.cursor()
                                cursor.execute(updatelogsql)
                                mydb.commit()
                            print("timeout")
                    else:
                        if len(openidlist) != 0:
                            temp2 = []
                            openids = ""
                            tempcount = 0
                            for i in range(len(openidlist)):
                                temp2.append(openidlist[i])
                                openids=openids+openidlist[i].encode('utf-8')+","
                                if len(temp2) == ONCENUM:
                                    print("len(temp2)=="+str(len(temp2)))
                                    tempcount = tempcount + 1
                                    openidlistid = str(uuid.uuid4())
                                    redisdb.hmset("openidsync:"+openidlistid,{
                                        "_id": openidlistid,
                                        "openidlist": openids,
                                        "logid": logid,
                                        "lastid": 0,
                                        "account_id":account_id,
                                        "org_id":org_id
                                    })
                                    redisdb.lpush("openid","openidsync:"+openidlistid)
                                    temp2 = []
                                    openids = ""
                            if len(temp2)>0:
                                openidlistid = str(uuid.uuid4())
                                redisdb.lpush("openid","openidsync:"+openidlistid)
                                redisdb.hmset("openidsync:"+openidlistid,{
                                    "_id": openidlistid,
                                    "openidlist": openids,
                                    "logid": logid,
                                    "lastid": 1,
                                    "account_id":account_id,
                                    "org_id":org_id
                                })
                                    #app.send_task('srjob.custinfo.custinfosync',args=[temp],queue='custinfosync')         

                        else:   #如果超时，返回None
                            redisdb.lpush("openid","openidsync:"+openidlistid)
                            redisdb.hmset("openidsync:"+openidlistid,{
                                "_id": openidlistid,
                                "openidlist": "",
                                "logid": logid,
                                "lastid": 1,
                                "account_id":account_id,
                                "org_id":org_id
                            })
                        break
                #time.sleep(3)

        else:
            if logid:
                updatelogsql = ("update sr_sys_schedule_log set statecode = 3 where id = %d" % logid)
                cursor = mydb.cursor()
                cursor.execute(updatelogsql)
                mydb.commit()
            print("timeout")

#while not finish:
    #conn.process_data_events()
if __name__ == "__main__":
    # 使用自定义参数运行
    # --beat同时开启beat模式，即运行按计划发送task的实例
    # 应确保全局只有一份同样的beat
    app.worker_main(["worker", "--loglevel=debug","-n","custsync.%h","-Qcustsync"])
