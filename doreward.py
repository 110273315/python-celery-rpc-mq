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
#import logging
#import logging.handlers
#import sys


ONCE_CAPACITY = 1

app = Celery("srjob.reward", broker=amqp_url)


platforms.C_FORCE_ROOT = True

app.conf.update(
    CELERY_TRACK_STARTED=True,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_IMPORTS = ("addsendapp","preparesendapp","dosendapp","addJob","addreward","addsendmail","addsendmsg","addsendsms","addtask","custinfosync","custsync","dosendmail","dosendmsg","dosendsms","findJob","preparereward","preparesendmail","preparesendmsg","preparesendsms","sessionclose","tagsync","tasks","usercheck",),
    CELERYBEAT_SCHEDULE={
        'reward-active-every-10-seconds': {
            'task': 'srjob.reward.active',
            'schedule': datetime.timedelta(seconds=240),
        }
    }
)

diff_time = time.timezone
def utc_now():
    return datetime.datetime.now() + datetime.timedelta(seconds=diff_time)



@app.task(name="srjob.reward.active")
def doreward():
    redisdb = ensure_redis()
    listlen = redisdb.llen("reward")

    for i in range(listlen):
        listid = redisdb.lindex("reward",i)
        try:
            task = redisdb.hgetall(listid)
            if task['status'] == 'ERROR' and task['isenable'] == '0' and task['prepare'] == '1':
                redisdb.hmset(listid,{"status": "running", "isenable": 1})
            elif task['status'] == 'running' and task['isenable'] == '1' and task['prepare'] == '1':
                rid = task['_id']
                synclistlen = redisdb.llen("rewardsync")
                mydb = connect()
                ensure_mysql()
                cursor = mydb.cursor()
                couponrpc = ensure_couponrpc()
                pointrpc = ensure_pointrpc()
                if task["queried"] == '0':
                    redisdb.hset(listid,'isenable',0)
                    campaignid = int(task['campaignid'])
                    updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                    cursor.execute(updatesql)
                    mydb.commit()
                    redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                else:
                    for j in range(synclistlen-1,-1,-1):
                        synclistid = redisdb.lindex("rewardsync",j)
                        reward = redisdb.hgetall(synclistid)
                        if not reward:
                            redisdb.lrem("rewardsync",1,synclistid)
                        else:
                            if reward["task_id"]==str(rid):
                                count = 0
                                reward = _decode_dict(reward)
                                activetime = reward["activetime"]
                                if datetime.datetime.strptime(activetime, "%Y-%m-%d %H:%M:%S") < datetime.datetime.now():
                                    redisdb.hset(listid,'isenable',0)
                                    if "username" in reward.keys():
                                        if reward["username"]:
                                            custname = reward["username"]
                                        else:
                                            custname = ""
                                    if "campaignid" in reward.keys():
                                        if reward["campaignid"] != '':
                                            campaignid = int(reward["campaignid"])
                                    if "pointnum" in reward.keys():
                                        if reward["pointnum"] != '':
                                            pointnum = int(reward["pointnum"])
                                    if "sendtype" in reward.keys():
                                        if reward["sendtype"] != '':
                                            sendtype = int(reward["sendtype"])
                                    if "couponid" in reward.keys():
                                        if reward["couponid"] != '':
                                            couponid = int(reward["couponid"])
                                    if "pointexdate" in reward.keys():
                                        if reward["pointexdate"] != '':
                                            pointexdate = reward["pointexdate"]
                                    if "userid" in reward.keys():
                                        if reward["userid"] != '':
                                            userid = int(reward["userid"])
                                    if "task_id" in reward.keys():
                                        if reward["task_id"] != '':
                                            task_id = int(reward["task_id"])
                                    if "rewardid" in reward.keys():
                                        if reward["rewardid"] != '':
                                            rewardid = reward["rewardid"]
                                    remark = "系统奖励"


                                    #发礼券
                                    if sendtype == 1:
                                        activenamesql = ("select title from sr_campaign where id = %d" % campaignid)
                                        cursor.execute(activenamesql)
                                        row = cursor.fetchone()
                                        if not row:
                                            break
                                        title = row[0]
                                        req = sr_customer_coupon_pb2.Message()
                                        req.header.sender="couponjob"
                                        req.header.sender_type="job"
                                        req.req_reward_coupon.couponid = couponid
                                        req.req_reward_coupon.custid = userid
                                        req.req_reward_coupon.activityname = title
                                        req.req_reward_coupon.quantity = 1
                                        req.req_reward_coupon.sendchannelcode = 9
                                        req.req_reward_coupon.applicablechannelcode = 4
                                        print("发礼券请求的数据:"+str(req)+"\r\n")
                                        datas = req.SerializeToString()
                                        cursor = mydb.cursor()
                                        repeats = 0
                                        repeatbycoupon(couponrpc,cursor,mydb,redisdb,datas,count,task_id,campaignid,userid,custname,synclistid,listid,repeats)

                                    #送积分
                                    elif sendtype == 2:
                                        req = sr_point_pb2.Message()
                                        req.header.sender="pointjob"
                                        req.header.sender_type="job"
                                        req.req_receipt_point.addednum = pointnum
                                        req.req_receipt_point.custid = userid
                                        req.req_receipt_point.duetime = pointexdate
                                        req.req_receipt_point.channelcode = 4
                                        req.req_receipt_point.typeid = 1
                                        req.req_receipt_point.remark = remark.decode("utf-8")
                                        print("送积分请求的数据:"+str(req)+"\r\n")
                                        datas = req.SerializeToString()
                                        repeats = 0
                                        #cursor = mydb.cursor()
                                        repeatbypoint(pointrpc,cursor,mydb,redisdb,datas,count,task_id,campaignid,userid,custname,synclistid,listid,repeats)
                                    #发礼券送积分
                                    else:
                                        activenamesql = ("select title from sr_campaign where id = %d" % campaignid)
                                        print(activenamesql+"\r\n")
                                        cursor.execute(activenamesql)
                                        row = cursor.fetchone()
                                        if not row:
                                            break
                                        title = row[0]
                                        req = sr_customer_coupon_pb2.Message()
                                        req.header.sender="couponjob"
                                        req.header.sender_type="job"
                                        req.req_reward_coupon.couponid = couponid
                                        req.req_reward_coupon.custid = userid
                                        req.req_reward_coupon.activityname = title
                                        req.req_reward_coupon.quantity = 1
                                        req.req_reward_coupon.sendchannelcode = 9
                                        req.req_reward_coupon.applicablechannelcode = 4
                                        print("发礼券请求的数据:"+str(req)+"\r\n")
                                        datas = req.SerializeToString()
                                        cursor = mydb.cursor()
                                        repeats = 0

                                        pointreq = sr_point_pb2.Message()
                                        pointreq.header.sender="pointjob"
                                        pointreq.header.sender_type="job"
                                        pointreq.req_receipt_point.addednum = pointnum
                                        pointreq.req_receipt_point.custid = userid
                                        pointreq.req_receipt_point.duetime = pointexdate
                                        pointreq.req_receipt_point.channelcode = 4
                                        pointreq.req_receipt_point.typeid = 1
                                        pointreq.req_receipt_point.remark = remark.decode("utf-8")
                                        print("送积分请求的数据:"+str(pointreq)+"\r\n")

                                        couponrepeat(couponrpc,pointrpc,cursor,mydb,datas,task_id,campaignid,userid,custname,repeats,count,synclistid,listid,redisdb,pointreq)

        except Exception as e:
            # 更新task状态
            redisdb.hmset(listid,{"status":"ERROR","isenable":0,"error":str(e),"err_time":utc_now()})
            raise





                                    

def repeatbycoupon(couponrpc,cursor,mydb,redisdb,datas,count,task_id,campaignid,userid,custname,synclistid,listid,repeats):
    if repeats < 3:
        data = couponrpc.call(datas,20)    #1 seconds timeout
        if data:
            reply = sr_customer_coupon_pb2.Message()
            reply.ParseFromString(data)
            print("发礼券返回的数据:"+str(reply)+"\r\n")
            errcode = reply.res_reward_coupon.errcode
            if errcode == 0:
                sql = ("INSERT INTO sr_rewards_job_docustids (id,jobid,campaignid,custid,custname,sendtype,rewardsstatus,pointsstatus,createdtime,rewardsendtime,pointsendtime,msgresultcoupon,msgresultpoint,errcode) VALUES (NULL,%d,%d,%d,\"%s\",1,1,0,NOW(),NOW(),NULL,NULL,NULL,0)" % (task_id,campaignid,userid,custname))
                cursor.execute(sql)
                mydb.commit()
                redisdb.delete(synclistid)
                redisdb.lrem("rewardsync",1,synclistid)
                redisdb.hincrby(listid,'downcount',-1)
                newreward = redisdb.hgetall(listid)

                if newreward and newreward["downcount"] == '0':
                    redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                    if newreward["queried"] == str(count):
                        updatesql = ("update sr_campaign set state = 3 WHERE id = %d" % (campaignid))
                    else:
                        updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                    cursor.execute(updatesql)
                    mydb.commit()
            else:
                if repeats == 2:
                    count = count + 1
                    sql = ("INSERT INTO sr_rewards_job_docustids (id,jobid,campaignid,custid,custname,sendtype,rewardsstatus,pointsstatus,createdtime,rewardsendtime,pointsendtime,msgresultcoupon,msgresultpoint,errcode) VALUES (NULL,%d,%d,%d,\"%s\",1,0,0,NOW(),NOW(),NULL,NULL,NULL,%d)" % (task_id,campaignid,userid,custname,errcode))
                    cursor.execute(sql)
                    mydb.commit()
                    redisdb.delete(synclistid)
                    redisdb.lrem("rewardsync",1,synclistid)
                    redisdb.hincrby(listid,'downcount',-1)
                    newreward = redisdb.hgetall(listid)

                    if newreward and newreward["downcount"] == '0':
                        redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                        if newreward["queried"] == str(count):
                            updatesql = ("update sr_campaign set state = 3 WHERE id = %d" % (campaignid))
                        else:
                            updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                        cursor.execute(updatesql)
                        mydb.commit()
                else:
                    repeats = repeats + 1
                    repeatbycoupon(couponrpc,cursor,mydb,redisdb,datas,count,task_id,campaignid,userid,custname,synclistid,listid,repeats)

        else:
            if repeats == 2:
                count = count + 1
                sql = ("INSERT INTO sr_rewards_job_docustids (id,jobid,campaignid,custid,custname,sendtype,rewardsstatus,pointsstatus,createdtime,rewardsendtime,pointsendtime,msgresultcoupon,msgresultpoint,errcode) VALUES (NULL,%d,%d,%d,\"%s\",1,0,0,NOW(),NOW(),NULL,NULL,NULL,11)" % (task_id,campaignid,userid,custname))
                redisdb.delete(synclistid)
                cursor.execute(sql)
                mydb.commit()
                redisdb.lrem("rewardsync",1,synclistid)
                redisdb.hincrby(listid,'downcount',-1)
                newreward = redisdb.hgetall(listid)

                if newreward and newreward["downcount"] == '0':
                    redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                    if newreward["queried"] == str(count):
                        updatesql = ("update sr_campaign set state = 3 WHERE id = %d" % (campaignid))
                    else:
                        updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                    cursor.execute(updatesql)
                    mydb.commit()
                print("发礼券RPC Request TimeOut\r\n")
            else:
                repeats = repeats + 1
                repeatbycoupon(couponrpc,cursor,mydb,redisdb,datas,count,task_id,campaignid,userid,custname,synclistid,listid,repeats)

def repeatbypoint(pointrpc,cursor,mydb,redisdb,datas,count,task_id,campaignid,userid,custname,synclistid,listid,repeats):
    if repeats < 3:
        data = pointrpc.call(datas,20)    #1 seconds timeout
        if data:
            reply = sr_point_pb2.Message()
            reply.ParseFromString(data)
            print("送积分返回的数据:"+str(reply)+"\r\n")
            errcode = reply.res_receipt_point.errcode
            if errcode == 0:
                sql = ("INSERT INTO sr_rewards_job_docustids (id,jobid,campaignid,custid,custname,sendtype,rewardsstatus,pointsstatus,createdtime,rewardsendtime,pointsendtime,msgresultcoupon,msgresultpoint,errcode) VALUES (NULL,%d,%d,%d,\"%s\",2,0,1,NOW(),NULL,NOW(),NULL,NULL,0)" % (task_id,campaignid,userid,custname))
                cursor.execute(sql)
                mydb.commit()
                redisdb.delete(synclistid)
                redisdb.lrem("rewardsync",1,synclistid)
                redisdb.hincrby(listid,'downcount',-1)
                newreward = redisdb.hgetall(listid)
                if newreward and newreward["downcount"] == '0':
                    redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                    if newreward["queried"] == str(count):
                        updatesql = ("update sr_campaign set state = 3 WHERE id = %d" % (campaignid))
                    else:
                        updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                    cursor.execute(updatesql)
                    mydb.commit()
            else:
                if repeats == 2:
                    count = count + 1
                    sql = ("INSERT INTO sr_rewards_job_docustids (id,jobid,campaignid,custid,custname,sendtype,rewardsstatus,pointsstatus,createdtime,rewardsendtime,pointsendtime,msgresultcoupon,msgresultpoint,errcode) VALUES (NULL,%d,%d,%d,\"%s\",2,0,0,NOW(),NULL,NOW(),NULL,NULL,%d)" % (task_id,campaignid,userid,custname,errcode))
                    cursor.execute(sql)
                    mydb.commit()
                    redisdb.delete(synclistid)
                    redisdb.lrem("rewardsync",1,synclistid)
                    redisdb.hincrby(listid,'downcount',-1)
                    newreward = redisdb.hgetall(listid)
                    if newreward and newreward["downcount"] == '0':
                        redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                        if newreward["queried"] == str(count):
                            updatesql = ("update sr_campaign set state = 3 WHERE id = %d" % (campaignid))
                        else:
                            updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                        cursor.execute(updatesql)
                        mydb.commit()
                else:
                    repeats = repeats + 1
                    repeatbypoint(pointrpc,cursor,mydb,redisdb,datas,count,task_id,campaignid,userid,custname,synclistid,listid,repeats)

        else:
            if repeats == 2:
                count = count + 1
                sql = ("INSERT INTO sr_rewards_job_docustids (id,jobid,campaignid,custid,custname,sendtype,rewardsstatus,pointsstatus,createdtime,rewardsendtime,pointsendtime,msgresultcoupon,msgresultpoint,errcode) VALUES (NULL,%d,%d,%d,\"%s\",2,0,0,NOW(),NULL,NOW(),NULL,NULL,11)" % (task_id,campaignid,userid,custname))
                redisdb.delete(synclistid)
                cursor.execute(sql)
                mydb.commit()
                redisdb.lrem("rewardsync",1,synclistid)
                redisdb.hincrby(listid,'downcount',-1)
                newreward = redisdb.hgetall(listid)

                if newreward and newreward["downcount"] == '0':
                    redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                    if newreward["queried"] == str(count):
                        updatesql = ("update sr_campaign set state = 3 WHERE id = %d" % (campaignid))
                    else:
                        updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                    cursor.execute(updatesql)
                    mydb.commit()
                print("送积分RPC Request TimeOut\r\n")
            else:
                repeats = repeats + 1
                repeatbypoint(pointrpc,cursor,mydb,redisdb,datas,count,task_id,campaignid,userid,custname,synclistid,listid,repeats)




def couponrepeat(couponrpc,pointrpc,cursor,mydb,datas,task_id,campaignid,userid,custname,repeats,count,synclistid,listid,redisdb,pointreq):
    if repeats < 3:
        data = couponrpc.call(datas,20)    #1 seconds timeout
        if data:
            reply = sr_customer_coupon_pb2.Message()
            reply.ParseFromString(data)
            print("发礼券返回的数据:"+str(reply)+"\r\n")
            errcode = reply.res_reward_coupon.errcode
            if errcode == 0:
                sql = ("INSERT INTO sr_rewards_job_docustids (id,jobid,campaignid,custid,custname,sendtype,rewardsstatus,pointsstatus,createdtime,rewardsendtime,pointsendtime,msgresultcoupon,msgresultpoint,errcode) VALUES (NULL,%d,%d,%d,\"%s\",3,1,0,NOW(),NOW(),NULL,NULL,NULL,0)" % (task_id,campaignid,userid,custname))
                cursor.execute(sql)
                docustid = cursor.lastrowid
                mydb.commit()
                print("送积分请求的数据:"+str(pointreq)+"\r\n")
                datas = pointreq.SerializeToString()
                repeats = 0
                pointrepeat(pointrpc,cursor,mydb,redisdb,datas,count,docustid,synclistid,campaignid,listid,repeats)
            else:
                if repeats == 2:
                    sql = ("INSERT INTO sr_rewards_job_docustids (id,jobid,campaignid,custid,custname,sendtype,rewardsstatus,pointsstatus,createdtime,rewardsendtime,pointsendtime,msgresultcoupon,msgresultpoint,errcode) VALUES (NULL,%d,%d,%d,\"%s\",3,0,0,NOW(),NOW(),NULL,NULL,NULL,%d)" % (task_id,campaignid,userid,custname,errcode))
                    cursor.execute(sql)
                    docustid = cursor.lastrowid
                    mydb.commit()
                    print("送积分请求的数据:"+str(pointreq)+"\r\n")
                    datas = pointreq.SerializeToString()
                    repeats = 0
                    pointrepeat(pointrpc,cursor,mydb,redisdb,datas,count,docustid,synclistid,campaignid,listid,repeats)
                else:
                    repeats = repeats + 1
                    couponrepeat(couponrpc,pointrpc,cursor,mydb,datas,task_id,campaignid,userid,custname,repeats,count,synclistid,listid,redisdb,pointreq)
        else:
            if repeats == 2:
                sql = ("INSERT INTO sr_rewards_job_docustids (id,jobid,campaignid,custid,custname,sendtype,rewardsstatus,pointsstatus,createdtime,rewardsendtime,pointsendtime,msgresultcoupon,msgresultpoint,errcode) VALUES (NULL,%d,%d,%d,\"%s\",3,0,0,NOW(),NOW(),NULL,NULL,NULL,11)" % (task_id,campaignid,userid,custname))
                cursor.execute(sql)
                docustid = cursor.lastrowid
                mydb.commit()
                print("送积分请求的数据:"+str(pointreq)+"\r\n")
                datas = pointreq.SerializeToString()
                repeats = 0
                pointrepeat(pointrpc,cursor,mydb,redisdb,datas,count,docustid,synclistid,campaignid,listid,repeats)
            else:
                repeats = repeats + 1
                couponrepeat(couponrpc,pointrpc,cursor,mydb,datas,task_id,campaignid,userid,custname,repeats,count,synclistid,listid,redisdb,pointreq)


def pointrepeat(pointrpc,cursor,mydb,redisdb,datas,count,docustid,synclistid,campaignid,listid,repeats):
    if repeats < 3:
        data = pointrpc.call(datas,20)    #1 seconds timeout
        if data:
            reply = sr_point_pb2.Message()
            reply.ParseFromString(data)
            print("送积分返回的数据:"+str(reply)+"\r\n")
            errcode = reply.res_receipt_point.errcode
            print("errcode=="+str(errcode)+"\r\n")
            if errcode == 0:
                updatesql = ("UPDATE sr_rewards_job_docustids SET pointsstatus = 1 WHERE id = %d" % docustid)
                print("updatesql=="+updatesql+"\r\n")
                redisdb.delete(synclistid)
                cursor.execute(updatesql)
                mydb.commit()
                redisdb.lrem("rewardsync",1,synclistid)
                redisdb.hincrby(listid,'downcount',-1)
                newreward = redisdb.hgetall(listid)

                if newreward and newreward["downcount"] == '0':
                    redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                    if newreward["queried"] == str(count):
                        updatesql = ("update sr_campaign set state = 3 WHERE id = %d" % (campaignid))
                    else:
                        updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                    cursor.execute(updatesql)
                    mydb.commit()
            else:
                if repeats == 2:
                    count = count + 1
                    updatesql = ("UPDATE sr_rewards_job_docustids SET pointsstatus = 0 WHERE id = %d" % docustid)
                    print("updatesql=="+updatesql+"\r\n")
                    redisdb.delete(synclistid)
                    cursor.execute(updatesql)
                    mydb.commit()
                    redisdb.lrem("rewardsync",1,synclistid)
                    redisdb.hincrby(listid,'downcount',-1)
                    newreward = redisdb.hgetall(listid)

                    if newreward and newreward["downcount"] == '0':
                        redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                        if newreward["queried"] == str(count):
                            updatesql = ("update sr_campaign set state = 3 WHERE id = %d" % (campaignid))
                        else:
                            updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                        cursor.execute(updatesql)
                        mydb.commit()
                else:
                    repeats = repeats + 1
                    pointrepeat(pointrpc,cursor,mydb,redisdb,datas,count,docustid,synclistid,campaignid,listid,repeats)

        else:
            if repeats == 2:
                count = count + 1
                sql = ("UPDATE sr_rewards_job_docustids SET pointsstatus = 0 WHERE id = %d" % docustid)
                redisdb.delete(synclistid)
                cursor.execute(sql)
                mydb.commit()
                redisdb.lrem("rewardsync",1,synclistid)
                redisdb.hincrby(listid,'downcount',-1)
                newreward = redisdb.hgetall(listid)


                if newreward['downcount'] == '0':
                    print("ssssss")
                    redisdb.hmset(listid,{"status":"SUCCESS", "end_time":utc_now()})
                    if newreward["queried"] == str(count):
                        updatesql = ("update sr_campaign set state = 3 WHERE id = %d" % (campaignid))
                    else:
                        updatesql = ("update sr_campaign set state = 4 WHERE id = %d" % (campaignid))
                    cursor.execute(updatesql)
                    mydb.commit()
                print("送积分RPC Request TimeOut\r\n")
            else:
                repeats = repeats + 1
                pointrepeat(pointrpc,cursor,mydb,redisdb,datas,count,docustid,synclistid,campaignid,listid,repeats)

            
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
    app.worker_main(["worker", "--beat","--loglevel=debug","-n","doreward.%h","-s","./sche-doreward"])