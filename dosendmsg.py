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
import sr_customer_coupon_pb2
import sr_point_pb2

ONCE_CAPACITY = 1

app = Celery("srjob.sendmsg", broker=amqp_url)


platforms.C_FORCE_ROOT = True

app.conf.update(
    CELERY_TRACK_STARTED=True,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_IMPORTS = ("addsendapp","preparesendapp","dosendapp","addJob","addreward","addsendmail","addsendmsg","addsendsms","addtask","custinfosync","custsync","doreward","dosendmail","dosendsms","findJob","preparereward","preparesendmail","preparesendmsg","preparesendsms","sessionclose","tagsync","tasks","usercheck",),
    CELERYBEAT_SCHEDULE={
        'reward-active-every-10-seconds': {
            'task': 'srjob.sendmsg.active',
            'schedule': datetime.timedelta(seconds=240),
        }
    }
)

diff_time = time.timezone
def utc_now():
    return datetime.datetime.now() + datetime.timedelta(seconds=diff_time)


@app.task(name="srjob.sendmsg.active")
def dosendmsg():
    redisdb = ensure_redis()
    sendmsgrpc = ensure_sendmsgrpc()
    listlen = redisdb.llen("sendmsg")
    for i in range(0, listlen):
        listid = redisdb.lindex("sendmsg",i)
        task = redisdb.hgetall(listid)
        try:
            if task['status'] == 'running' and task['prepare'] == '1':
                rid = task['_id']
                synclistlen = redisdb.llen("sendmsgsync")
                mydb = connect()
                ensure_mysql()
                cursor = mydb.cursor()
                if task["queried"] == '0':
                    campaignid = int(task['campaignid'])
                    updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                    cursor.execute(updatesql)
                    mydb.commit()
                    redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                else:
                    for j in range(synclistlen-1,-1,-1):
                        synclistid = redisdb.lindex("sendmsgsync",j)
                        sendmsg = redisdb.hgetall(synclistid)
                        if sendmsg['task_id']==str(rid):
                            count = 0
                            sendmsg = _decode_dict(sendmsg)
                            activetime = datetime.datetime.strptime(sendmsg["activetime"], "%Y-%m-%d %H:%M:%S")
                            if activetime < datetime.datetime.now():
                                if "sendaccount" in sendmsg.keys():
                                    sendaccount = sendmsg["sendaccount"]
                                if "openid" in sendmsg.keys():
                                    openids = sendmsg["openid"][:-1].split(',')
                                if "wechattype" in sendmsg.keys():
                                    wechattype = int(sendmsg["wechattype"])
                                if "content" in sendmsg.keys():
                                    content = sendmsg["content"]
                                if "task_id" in sendmsg.keys():
                                    task_id = int(sendmsg["task_id"])
                                if "sendmsgid" in sendmsg.keys():
                                    sendmsgid = sendmsg["sendmsgid"]
                                if "campaignid" in sendmsg.keys():
                                    campaignid = int(sendmsg["campaignid"])
                                if "custname" in sendmsg.keys():
                                    custname = sendmsg["custname"]
                                    if custname:
                                        custname = custname.decode('utf-8')
                                    else:
                                        custname = ""
                                if "nickname" in sendmsg.keys():
                                    nickname = sendmsg["nickname"]
                                if "photo" in sendmsg.keys():
                                    photo = sendmsg["photo"]
                                if "custid" in sendmsg.keys():
                                    custid = int(sendmsg["custid"])

                                req = cf_wechat_pb2.Message()
                                req.header.sender="sendmsg"
                                req.header.sender_type="job"
                                req.req_group_message_send.account_id = sendaccount
                                msgcontent = req.req_group_message_send.message_content.add()
                                print(wechattype)
                                if wechattype == 3:
                                    msgcontent.type = 2
                                    msgcontent.content = content.decode('utf-8')
                                elif wechattype == 4:
                                    msgcontent.type = 3
                                    msgcontent.resource_id = content.decode('utf-8')
                                elif wechattype == 5:
                                    msgcontent.type = 6
                                    videocontent = content.decode('utf-8').split('@filename@')
                                    msgcontent.resource_id = videocontent[0]
                                    msgcontent.content = '{"title":"'+videocontent[1]+'","description":"'+videocontent[1]+'"}'
                                else:
                                    msgcontent.type = 1
                                    msgcontent.resource_id = content.decode('utf-8')
                                if len(openids)==1:
                                    condition = req.req_group_message_send.customer_search_condition.add()
                                    condition.cf_account_id = sendaccount
                                    condition.wechat_open_id = openids[0].decode('utf-8')
                                    condition = req.req_group_message_send.customer_search_condition.add()
                                    condition.cf_account_id = sendaccount
                                    condition.wechat_open_id = openids[0].decode('utf-8')
                                else:
                                    for openid in openids:
                                        condition = req.req_group_message_send.customer_search_condition.add()
                                        condition.cf_account_id = sendaccount
                                        condition.wechat_open_id = openid.decode('utf-8')
                                print(req)
                                print(content)
                                datas = req.SerializeToString()
                                repeats = 0
                                msgid = 0
                                resendmsg(sendmsgrpc,cursor,mydb,redisdb,datas,count,campaignid,msgid,synclistid,listid,repeats)
        except Exception as e:
            # 更新task状态
            print(str(e))
            raise



def resendmsg(sendmsgrpc,cursor,mydb,redisdb,datas,count,campaignid,msgid,synclistid,listid,repeats):
    if repeats < 3:
        data = sendmsgrpc.call(datas,30)    #1 seconds timeout
        if data:
            reply = cf_wechat_pb2.Message()
            reply.ParseFromString(data)
            print(reply)
            errcode = reply.res_group_message_send.errcode
            msgid = reply.res_group_message_send.msg_id
            if errcode==0:
                print("repeats=="+str(repeats))
                print("msgid==="+str(msgid))
                sql = ("INSERT INTO sr_campaign_wechatpush_result (id,campaignid,msgid,errcode,totalcount,filtercount,sentcount,errorcount) VALUES (NULL,%d,%d,0,0,0,0,0)" % (campaignid,msgid))
                print("sql==="+sql)
                cursor.execute(sql)
                mydb.commit()
                redisdb.delete(synclistid)
                redisdb.lrem("sendmsgsync",1,synclistid)
                redisdb.hincrby(listid,'downcount',-1)
                newsendmsg = redisdb.hgetall(listid)
                if newsendmsg["downcount"] == '0':
                    redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                    if newsendmsg["queried"] == str(count):
                        updatesql = ("update sr_campaign set state = 3 WHERE id = %d" % (campaignid))
                    else:
                        updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))

                    cursor.execute(updatesql)
                    mydb.commit()
            else:
                if repeats == 2:
                    count = count + 1
                    sql = ("INSERT INTO sr_campaign_wechatpush_result (id,campaignid,msgid,errcode,totalcount,filtercount,sentcount,errorcount) VALUES (NULL,%d,NULL,%d,0,0,0,0)" % (campaignid,errcode))
                    cursor.execute(sql)
                    mydb.commit()
                    redisdb.delete(synclistid)
                    redisdb.lrem("sendmsgsync",1,synclistid)
                    redisdb.hincrby(listid,'downcount',-1)
                    newsendmsg = redisdb.hgetall(listid)
                    if newsendmsg["downcount"] == '0':
                        redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                        if newsendmsg["queried"] == str(count):
                            updatesql = ("update sr_campaign set state = 3 WHERE id = %d" % (campaignid))
                        else:
                            updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                        cursor.execute(updatesql)
                        mydb.commit()
                else:
                    repeats = repeats + 1
                    resendmsg(sendmsgrpc,cursor,mydb,redisdb,datas,count,campaignid,msgid,synclistid,listid,repeats)
        else:
            if repeats == 2:
                sql = ("INSERT INTO sr_campaign_wechatpush_result (id,campaignid,msgid,errcode,totalcount,filtercount,sentcount,errorcount) VALUES (NULL,%d,NULL,2,0,0,0,0)" % (campaignid))
                cursor.execute(sql)
                mydb.commit()
                count = count + 1
                redisdb.delete(synclistid)
                redisdb.lrem("sendmsgsync",1,synclistid)
                redisdb.hincrby(listid,'downcount',-1)
                newsendmsg = redisdb.hgetall(listid)
                if newsendmsg["downcount"] == '0':
                    redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                    if newsendmsg["queried"] == str(count):
                        updatesql = ("update sr_campaign set state = 3 WHERE id = %d" % (campaignid))
                    else:
                        updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                    cursor.execute(updatesql)
                    mydb.commit()
                print("timeout")
            else:
                repeats = repeats + 1
                resendmsg(sendmsgrpc,cursor,mydb,redisdb,datas,count,campaignid,msgid,synclistid,listid,repeats)


            
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
    app.worker_main(["worker", "--beat", "--loglevel=debug","-n","dosendmsg.%h","-s","./sche-dosendmsg"])