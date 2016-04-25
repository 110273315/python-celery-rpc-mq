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
import sr_job_task_pb2
import threading


app = Celery("srjob.session", broker=amqp_url)


platforms.C_FORCE_ROOT = True

app.conf.update(
    CELERY_TRACK_STARTED=True,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_IMPORTS = ("addsendapp","preparesendapp","dosendapp","addJob","addreward","addsendmail","addsendmsg","addsendsms","addtask","custinfosync","custsync","doreward","dosendmail","dosendmsg","dosendsms","findJob","preparereward","preparesendmail","preparesendmsg","preparesendsms","tagsync","tasks","usercheck",)
)


@app.task(name="srjob.session.multicustsessionclose")
def multicustsessionclose():
    #创建守护线程，处理amqp事件
    #程序会等待所有非守护线程结束，才会退出
    #守护线程在程序退出时，自动结束
    print("sessionclosesessionclosesessionclose")
    mydb = connect()
    ensure_mysql()
    sessionrpc = ensure_sessionrpc()
    sql = "SELECT id,visitorid,accountid,lasttime,statuscode,killtype,createdtime FROM sr_multicustservice_session where statuscode != 3"
    cursor = mydb.cursor()
    #cursor = mydb.cursor()
    cursor.execute(sql)
    flag = 0
    updatesql = []
    updatesql1 = []
    dic = {}
    dic1 = {}
    while True:
        row = cursor.fetchone()
        if not row:
            break
        id = row[0]
        openid = row[1]
        accountid = row[2]
        lasttime = row[3]
        statuscode = row[4]
        killtype = row[5]
        createdtime = row[6]
        print(statuscode)
        print(createdtime)
        print(lasttime)
        if statuscode == 1:
            if createdtime < (datetime.datetime.now() + datetime.timedelta(hours=-2)):
                sql1 = ("UPDATE sr_multicustservice_session SET statuscode=3,killtype=3,endtime=now() where id = %d" % id)
                if sql1 not in updatesql:
                    dic[id] = sql1
                    print("sql1==="+sql1)
                    updatesql.append(sql1)
                #cursor.execute(sql1)
                #mydb.commit()
                #req = sr_job_task_pb2.Message()
                #req.header.sender="req_session_close"
                #req.header.sender_type="type1"
                #req.req_session_close.openid = openid
                #req.req_session_close.type = 3
                #req.req_session_close.accountid = accountid
                #data = req.SerializeToString()
                #sessionrpc.call(data,1)
                flag = 1

        if statuscode == 2:
            if lasttime < (datetime.datetime.now() + datetime.timedelta(minutes=-20)):
                sql2 = ("UPDATE sr_multicustservice_session SET statuscode=3,killtype=2,endtime=now() where id = %d" % id)
                if sql2 not in updatesql1:
                    dic1[id] = sql2
                    updatesql1.append(sql2)
                    print("sql2==="+sql2)
                #
                #cursor.execute(sql2)
                #mydb.commit()
                #req = sr_job_task_pb2.Message()
                #req.header.sender="req_session_close"
                #req.header.sender_type="type1"
                #req.req_session_close.openid = openid
                #req.req_session_close.type = 2
                #req.req_session_close.accountid = accountid
                #data = req.SerializeToString()
                #sessionrpc.call(data,1)
                flag = 1

    cursor = mydb.cursor()
    if len(dic)!=0:
        for key in dic:
            cursor.execute(dic[key])
            mydb.commit()
            req = sr_job_task_pb2.Message()
            req.header.sender="req_session_close"
            req.header.sender_type="type1"
            req.req_session_close.openid = str(key)
            req.req_session_close.type = 3
            req.req_session_close.accountid = accountid
            data = req.SerializeToString()
            sessionrpc.call(data,5)
            flag = 1
    if len(dic1)!=0:
        for ks in dic1:
            cursor.execute(dic1[ks])
            mydb.commit()
            req = sr_job_task_pb2.Message()
            req.header.sender="req_session_close"
            req.header.sender_type="type1"
            req.req_session_close.openid = str(ks)
            req.req_session_close.type = 2
            req.req_session_close.accountid = accountid
            print(req)
            data = req.SerializeToString()
            sessionrpc.call(data,5)
            flag = 1

    if flag:
        logsql = ("insert into sr_sys_schedule_log (taskid,taskname,exectime,statecode) VALUES (%d,\"%s\",NOW(),2)" % (27,"关闭多客服会话"))
        cursor.execute(logsql)
        mydb.commit()

	    

#while not finish:
    #conn.process_data_events()
if __name__ == "__main__":
    # 使用自定义参数运行
    # --beat同时开启beat模式，即运行按计划发送task的实例
    # 应确保全局只有一份同样的beat
    app.worker_main(["worker", "--loglevel=debug","-n","sessionclose.%h"])
