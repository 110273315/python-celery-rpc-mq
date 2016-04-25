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
import cf_app_pb2
import sys
reload(sys)
sys.setdefaultencoding('utf8')

ONCE_CAPACITY = 1

app = Celery("srjob.sendapp", broker=amqp_url)


platforms.C_FORCE_ROOT = True

app.conf.update(
    CELERY_TRACK_STARTED=True,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_IMPORTS = ("addsendapp","preparesendapp","addJob","addreward","addsendmail","addsendmsg","addsendsms","addtask","custinfosync","custsync","doreward","dosendsms","dosendmail","dosendmsg","findJob","preparereward","preparesendmail","preparesendmsg","preparesendsms","sessionclose","tagsync","tasks","usercheck",),
    CELERYBEAT_SCHEDULE={
        'srjob-sendapp-every-10-seconds': {
            'task': 'srjob.sendapp.active',
            'schedule': datetime.timedelta(seconds=240),
        }
    }
)

diff_time = time.timezone
def utc_now():
    return datetime.datetime.now() + datetime.timedelta(seconds=diff_time)


@app.task(name="srjob.sendapp.active")
def dosendapp():
    redisdb = ensure_redis()
    sapprpc = ensure_sendsapprpc()
    listlen = redisdb.llen("sendapp")
    for i in range(0, listlen):
        listid = redisdb.lindex("sendapp",i)
        try:
            task = redisdb.hgetall(listid)
            if task['status'] == 'ERROR' and task['isenable'] == '0' and task['prepare'] == '1':
                redisdb.hmset(listid,{"status": "running", "isenable": 1})
            if task['status'] == 'running' and task['isenable'] == '1' and task['prepare'] == '1':
                mydb = connect()
                ensure_mysql()
                cursor = mydb.cursor()
                rid = task['_id']
                synclistlen = redisdb.llen("sendappsync")
                if task["queried"] == '0':
                    redisdb.hset(listid,'isenable',0)
                    campaignid = int(task['campaignid'])
                    updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                    cursor.execute(updatesql)
                    mydb.commit()
                    redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                else:
                    for i in range(synclistlen-1,-1,-1):
                        synclistid = redisdb.lindex("sendappsync",i)
                        sendapp = redisdb.hgetall(synclistid)
                        if sendapp['task_id']==str(rid):
                            count = 0
                            sendapp = _decode_dict(sendapp)
                            activetime = sendapp["activetime"]
                            if datetime.datetime.strptime(activetime, "%Y-%m-%d %H:%M:%S") < datetime.datetime.now():
                                redisdb.hset(listid,'isenable',0)
                                if "sendaccount" in sendapp.keys():
                                    sendaccount = sendapp["sendaccount"]
                                if "content" in sendapp.keys():
                                    content = sendapp["content"]
                                if "activetime" in sendapp.keys():
                                    activetime = sendapp["activetime"]
                                if "task_id" in sendapp.keys():
                                    task_id = int(sendapp["task_id"])
                                if "sendappid" in sendapp.keys():
                                    sendappid = sendapp["sendappid"]
                                if "campaignid" in sendapp.keys():
                                    campaignid = int(sendapp["campaignid"])
                                if "custname" in sendapp.keys():
                                    custname = sendapp["custname"]
                                    if custname:
                                        custname = custname.decode('utf-8')
                                    else:
                                        custname = ""
                                if "custid" in sendapp.keys():
                                    custid = int(sendapp["custid"])
                                if "mobile" in sendapp.keys():
                                    mobile = sendapp["mobile"]
                                if "title" in sendapp.keys():
                                    title = sendapp["title"]
                                if "app_deviceid" in sendapp.keys():
                                    app_deviceid = sendapp["app_deviceid"]
                                if app_deviceid=="None":
                                    count = count + 1
                                    sql = ("INSERT INTO sr_campaign_apppush (id,campaignid,custid,custname,app_account,issatisfy,sendtime,result,errmsg,createdtime) VALUES (NULL,%d,%d,\"%s\",\"%s\",1,NOW(),0,'设备号不存在！',NOW())" % (campaignid,custid,custname,mobile))
                                    cursor.execute(sql)
                                    mydb.commit()
                                    redisdb.delete(synclistid)
                                    redisdb.lrem("sendappsync",1,synclistid)
                                    redisdb.hincrby(listid,'downcount',-1)
                                    newsendapp = redisdb.hgetall(listid)

                                    if newsendapp and newsendapp["downcount"] == '0':
                                        redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                                        if newsendapp["queried"] == str(count):
                                            updatesql = ("update sr_campaign set state = 3 WHERE id = %d" % (campaignid))
                                        else:
                                            updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                                        cursor.execute(updatesql)
                                        mydb.commit()
                                else:
                                    req = cf_app_pb2.Message()
                                    req.header.sender="sendapp"
                                    req.header.sender_type="job"
                                    req.req_push_message.account_id = sendaccount
                                    req.req_push_message.device_type.append(9)
                                    req.req_push_message.message_content.type = 9
                                    req.req_push_message.message_content.title = title.decode('utf-8')
                                    req.req_push_message.message_content.content = content.decode('utf-8')
                                    condition = req.req_push_message.customer_search_condition.add()
                                    condition.app_device_id = app_deviceid
                                    print(req)
                                    datas = req.SerializeToString()
                                    repeats = 0
                                    resendapp(sapprpc,cursor,mydb,redisdb,datas,count,campaignid,custid,custname,mobile,synclistid,listid,repeats)

        except Exception as e:
            # 更新task状态
            redisdb.hmset(listid,{"status":"ERROR","isenable":0,"error":str(e),"err_time":utc_now()})
            raise


def resendapp(sapprpc,cursor,mydb,redisdb,datas,count,campaignid,custid,custname,mobile,synclistid,listid,repeats):
    if repeats < 3:
        data = sapprpc.call(datas,60)    #1 seconds timeout
        if data:
            reply = cf_app_pb2.Message()
            reply.ParseFromString(data)
            print("sendappcontent=="+str(reply))
            errcode = reply.res_push_message.errcode
            errmsg = reply.res_push_message.errmsg
            print(errmsg)
            if errcode == 0:
                sql = ("INSERT INTO sr_campaign_apppush (id,campaignid,custid,custname,app_account,issatisfy,sendtime,result,errmsg,createdtime) VALUES (NULL,%d,%d,\"%s\",\"%s\",1,NOW(),1,'',NOW())" % (campaignid,custid,custname,mobile))
                print(sql)
                cursor.execute(sql)
                mydb.commit()
                redisdb.delete(synclistid)
                redisdb.lrem("sendappsync",1,synclistid)
                redisdb.hincrby(listid,'downcount',-1)
                newsendapp = redisdb.hgetall(listid)
                if newsendapp and newsendapp["downcount"] == '0':
                    redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                    if newsendapp["queried"] == str(count):
                        updatesql = ("update sr_campaign set state = 3 WHERE id = %d" % (campaignid))
                    else:
                        updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                    cursor.execute(updatesql)
                    mydb.commit()
            else:
                if repeats == 2:
                    count = count + 1
                    sql = ("INSERT INTO sr_campaign_apppush (id,campaignid,custid,custname,app_account,issatisfy,sendtime,result,errmsg,createdtime) VALUES (NULL,%d,%d,\"%s\",\"%s\",1,NOW(),0,\"%s\",NOW())" % (campaignid,custid,custname,mobile,str(errcode)))
                    print(sql)
                    cursor.execute(sql)
                    mydb.commit()
                    redisdb.delete(synclistid)
                    redisdb.lrem("sendappsync",1,synclistid)
                    redisdb.hincrby(listid,'downcount',-1)
                    newsendapp = redisdb.hgetall(listid)
                    if newsendapp and newsendapp["downcount"] == '0':
                        redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                        if newsendapp["queried"] == str(count):
                            updatesql = ("update sr_campaign set state = 3 WHERE id = %d" % (campaignid))
                        else:
                            updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                        cursor.execute(updatesql)
                        mydb.commit()
                else:
                    repeats = repeats + 1
                    resendapp(sapprpc,cursor,mydb,redisdb,datas,count,campaignid,custid,custname,mobile,synclistid,listid,repeats)

        else:
            if repeats == 2:
                count = count + 1
                sql = ("INSERT INTO sr_campaign_apppush (id,campaignid,custid,custname,app_account,issatisfy,sendtime,result,errmsg,createdtime) VALUES (NULL,%d,%d,\"%s\",\"%s\",1,NOW(),0,'系统超时！',NOW())" % (campaignid,custid,custname,mobile))
                cursor.execute(sql)
                mydb.commit()
                redisdb.delete(synclistid)
                redisdb.lrem("sendappsync",1,synclistid)
                redisdb.hincrby(listid,'downcount',-1)
                newsendapp = redisdb.hgetall(listid)
                if newsendapp and newsendapp["downcount"] == '0':
                    redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                    if newsendapp["queried"] == str(count):
                        updatesql = ("update sr_campaign set state = 3 WHERE id = %d" % (campaignid))
                    else:
                        updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                    cursor.execute(updatesql)
                    mydb.commit()
                print("timeout")
            else:
                repeats = repeats + 1
                resendapp(sapprpc,cursor,mydb,redisdb,datas,count,campaignid,custid,custname,mobile,synclistid,listid,repeats)

            
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
    app.worker_main(["worker", "--beat", "--loglevel=debug","-n","dosendapp.%h","-s","./sche-dosendapp"])