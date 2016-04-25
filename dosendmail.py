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
import cf_pb2


ONCE_CAPACITY = 1

app = Celery("srjob.sendmail", broker=amqp_url)


platforms.C_FORCE_ROOT = True

app.conf.update(
    CELERY_TRACK_STARTED=True,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_IMPORTS = ("addsendapp","preparesendapp","dosendapp","addJob","addreward","addsendmail","addsendmsg","addsendsms","addtask","custinfosync","custsync","doreward","dosendmsg","dosendsms","findJob","preparereward","preparesendmail","preparesendmsg","preparesendsms","sessionclose","tagsync","tasks","usercheck",),
    CELERYBEAT_SCHEDULE={
        'sendmail-active-every-10-seconds': {
            'task': 'srjob.sendmail.active',
            'schedule': datetime.timedelta(seconds=240),
        }
    }
)

diff_time = time.timezone
def utc_now():
    return datetime.datetime.now() + datetime.timedelta(seconds=diff_time)


@app.task(name="srjob.sendmail.active")
def dosendmail():
    redisdb = ensure_redis()
    smailrpc = ensure_sendsmailrpc()
    listlen = redisdb.llen("sendmail")

    for i in range(0, listlen):
        listid = redisdb.lindex("sendmail",i)
        try:
            task = redisdb.hgetall(listid)
            if task['status'] == 'ERROR' and task['isenable'] == '0' and task['prepare'] == '1':
                redisdb.hmset(listid,{"status": "running", "isenable": 1})
            if task['status'] == 'running' and task['isenable'] == '1' and task['prepare'] == '1':
                mydb = connect()
                ensure_mysql()
                cursor = mydb.cursor()
                rid = task['_id']
                synclistlen = redisdb.llen("sendmailsync")
                if task["queried"] == '0':
                    redisdb.hset(listid,'isenable',0)
                    campaignid = int(task['campaignid'])
                    updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                    cursor.execute(updatesql)
                    mydb.commit()
                    redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                else:
                    for i in range(synclistlen-1,-1,-1):
                        synclistid = redisdb.lindex("sendmailsync",i)
                        sendmail = redisdb.hgetall(synclistid)
                        if sendmail['task_id']==str(rid):
                            count = 0
                            sendmail = _decode_dict(sendmail)
                            activetime = sendmail["activetime"]
                            if datetime.datetime.strptime(activetime, "%Y-%m-%d %H:%M:%S") < datetime.datetime.now():
                                redisdb.hset(listid,'isenable',0)
                                if "sendaccount" in sendmail.keys():
                                    sendaccount = sendmail["sendaccount"]
                                if "content" in sendmail.keys():
                                    content = sendmail["content"]
                                if "activetime" in sendmail.keys():
                                    activetime = sendmail["activetime"]
                                if "task_id" in sendmail.keys():
                                    task_id = int(sendmail["task_id"])
                                if "sendmailid" in sendmail.keys():
                                    sendmailid = sendmail["sendmailid"]
                                if "campaignid" in sendmail.keys():
                                    campaignid = int(sendmail["campaignid"])
                                if "custname" in sendmail.keys():
                                    custname = sendmail["custname"]
                                    if custname:
                                        custname = custname.decode('utf-8')
                                    else:
                                        custname = ""
                                if "custid" in sendmail.keys():
                                    custid = int(sendmail["custid"])
                                if "emailaddress" in sendmail.keys():
                                    emailaddress = sendmail["emailaddress"]

                                if emailaddress=="None":
                                    count = count + 1
                                    sql = ("INSERT INTO sr_campaign_emailpush (id,campaignid,custid,custname,email,sendtime,result,issatisfy,createdtime) VALUES (NULL,%d,%d,\"%s\",NULL,NOW(),0,1,NOW())" % (campaignid,custid,custname))
                                    cursor.execute(sql)
                                    mydb.commit()
                                    redisdb.delete(synclistid)
                                    redisdb.lrem("sendmailsync",1,synclistid)
                                    redisdb.hincrby(listid,'downcount',-1)
                                    newsendmail = redisdb.hgetall(listid)
                                    if newsendmail and newsendmail["downcount"] == '0':
                                        redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                                        if newsendmail["queried"] == str(count):
                                            updatesql = ("update sr_campaign set state = 3 WHERE id = %d" % (campaignid))
                                        else:
                                            updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                                        cursor.execute(updatesql)
                                        mydb.commit()
                                else:
                                    req = cf_pb2.Message()
                                    req.header.sender="sendmail"
                                    req.header.sender_type="job"
                                    req.req_send_text.account_id = sendaccount
                                    req.req_send_text.content = content.decode('utf-8')
                                    condition = req.req_send_text.customer_search_condition.add()
                                    condition.cf_account_id = sendaccount
                                    condition.email = emailaddress
                                    print(req)
                                    datas = req.SerializeToString()
                                    repeats = 0
                                    resendmail(smailrpc,cursor,mydb,redisdb,datas,count,campaignid,custid,custname,emailaddress,synclistid,listid,repeats)

        except Exception as e:
            # 更新task状态
            redisdb.hmset(listid,{"status":"ERROR","isenable":0,"error":str(e),"err_time":utc_now()})
            raise




def resendmail(smailrpc,cursor,mydb,redisdb,datas,count,campaignid,custid,custname,emailaddress,synclistid,listid,repeats):
    if repeats < 3:
        data = smailrpc.call(datas,30)    #1 seconds timeout
        if data:
            reply = cf_pb2.Message()
            reply.ParseFromString(data)
            print(reply)
            errcode = reply.res_send_text.errcode
            if errcode == 0:
                sql = ("INSERT INTO sr_campaign_emailpush (id,campaignid,custid,custname,email,sendtime,result,issatisfy,createdtime) VALUES (NULL,%d,%d,\"%s\",\"%s\",NOW(),1,1,NOW())" % (campaignid,custid,custname,emailaddress))
                cursor.execute(sql)
                mydb.commit()
                redisdb.delete(synclistid)
                redisdb.lrem("sendmailsync",1,synclistid)
                redisdb.hincrby(listid,'downcount',-1)
                newsendmail = redisdb.hgetall(listid)
                if newsendmail and newsendmail["downcount"] == '0':
                    redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                    if newsendmail["queried"] == str(count):
                        updatesql = ("update sr_campaign set state = 3 WHERE id = %d" % (campaignid))
                    else:
                        updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                    cursor.execute(updatesql)
                    mydb.commit()
            else:
                if repeats == 2:
                    count = count + 1
                    sql = ("INSERT INTO sr_campaign_emailpush (id,campaignid,custid,custname,email,sendtime,result,issatisfy,createdtime) VALUES (NULL,%d,%d,\"%s\",\"%s\",NOW(),0,1,NOW())" % (campaignid,custid,custname,emailaddress))
                    cursor.execute(sql)
                    mydb.commit()
                    redisdb.delete(synclistid)
                    redisdb.lrem("sendmailsync",1,synclistid)
                    redisdb.hincrby(listid,'downcount',-1)
                    newsendmail = redisdb.hgetall(listid)
                    if newsendmail and newsendmail["downcount"] == '0':
                        redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                        if newsendmail["queried"] == str(count):
                            updatesql = ("update sr_campaign set state = 3 WHERE id = %d" % (campaignid))
                        else:
                            updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                        cursor.execute(updatesql)
                        mydb.commit()
                else:
                    repeats = repeats + 1
                    resendmail(smailrpc,cursor,mydb,redisdb,datas,count,campaignid,custid,custname,emailaddress,synclistid,listid,repeats)

        else:
            if repeats == 2:
                count = count + 1
                sql = ("INSERT INTO sr_campaign_emailpush (id,campaignid,custid,custname,email,sendtime,result,issatisfy,createdtime) VALUES (NULL,%d,%d,\"%s\",\"%s\",NOW(),0,1,NOW())" % (campaignid,custid,custname,emailaddress))
                cursor.execute(sql)
                mydb.commit()
                redisdb.delete(synclistid)
                redisdb.lrem("sendmailsync",1,synclistid)
                redisdb.hincrby(listid,'downcount',-1)
                newsendmail = redisdb.hgetall(listid)
                if newsendmail and newsendmail["downcount"] == '0':
                    redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                    if newsendmail["queried"] == str(count):
                        updatesql = ("update sr_campaign set state = 3 WHERE id = %d" % (campaignid))
                    else:
                        updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                    cursor.execute(updatesql)
                    mydb.commit()
                print("timeout")
            else:
                repeats = repeats + 1
                resendmail(smailrpc,cursor,mydb,redisdb,datas,count,campaignid,custid,custname,emailaddress,synclistid,listid,repeats)
            
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
    app.worker_main(["worker", "--beat", "--loglevel=debug","-n","dosendmail.%h","-s","./sche-dosendmail"])