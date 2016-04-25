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
import redis
import string




app = Celery("srjob.custinfo", broker=amqp_url)


platforms.C_FORCE_ROOT = True

app.conf.update(
    CELERY_ENABLE_UTC = True,
    CELERY_TIMEZONE = 'Asia/Shanghai',
    CELERY_TRACK_STARTED=True,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_IMPORTS = ("addsendapp","preparesendapp","dosendapp","addJob","addreward","addsendmail","addsendmsg","addsendsms","addtask","custsync","doreward","dosendmail","dosendmsg","dosendsms","findJob","preparereward","preparesendmail","preparesendmsg","preparesendsms","sessionclose","tagsync","tasks","usercheck",),
    CELERYBEAT_SCHEDULE={
        'custinfosync-every-60-seconds': {
            'task': 'srjob.custinfo.custinfosync',
            'schedule': datetime.timedelta(seconds=240),
        }
    }
)

diff_time = time.timezone
def utc_now():
    return datetime.datetime.now() + datetime.timedelta(seconds=diff_time)


@app.task(name="srjob.custinfo.custinfosync")
def custinfosync():
    #创建守护线程，处理amqp事件
    #程序会等待所有非守护线程结束，才会退出
    #守护线程在程序退出时，自动结束
    mydb = connect()
    ensure_mysql()
    rpc = ensure_rpc()
    redisdb = ensure_redis()
    rediscustdb = ensure_cust_redis()
    #print(openidlist)

    cursor = mydb.cursor()
    listlen = redisdb.llen("openid")
    for i in range(listlen-1,-1,-1):
        listid = redisdb.lindex("openid",i)
        openidObj = redisdb.hgetall(listid)
        if openidObj:
            openidlistid = openidObj["_id"]
            openidlist = openidObj["openidlist"][:-1].split(',')
            account_id = openidObj["account_id"]
            org_id = openidObj["org_id"]
            logid = int(openidObj["logid"])
            lastid = int(openidObj["lastid"])
            if lastid:
                count = 0
                templen = redisdb.llen("openid")
                for j in range(0, templen):
                    tempid = redisdb.lindex("openid",j)
                    tempopenid = redisdb.hgetall(tempid)
                    temp_account_id = tempopenid["account_id"]
                    temp_logid = int(tempopenid["logid"])
                    if temp_logid==logid and temp_account_id==account_id:
                        count = count + 1
                print("count = " + str(count))
                if count != 1:
                    continue
            if len(openidlist)==0:
                updatelogsql = ("update sr_sys_schedule_log set statecode = 2 where id = %d" % logid)
                cursor.execute(updatelogsql)
                mydb.commit()
                redisdb.delete(listid)
                redisdb.lrem("openid",1,listid)
                break
            req = cf_wechat_pb2.Message()
            req.header.sender="req_userinfo_query"
            req.header.sender_type="type1"
            req.req_userinfo_query.account_id = account_id
            for i in range(len(openidlist)):
                condition = "condition" + str(i)
                condition = req.req_userinfo_query.customer_search_condition.add()
                condition.cf_account_id=account_id
                condition.wechat_open_id=openidlist[i].encode('utf-8')
            print(req)
            data = req.SerializeToString()

    #第二个参数类型float，单位秒，缺省为None，不超时
            data = rpc.call(data,120)    #1 seconds timeout
            if data:
                reply = cf_wechat_pb2.Message()
                reply.ParseFromString(data)
                print(reply)
                errcode = reply.res_userinfo_query.errcode
                if errcode == 0:
                    for i in range(len(reply.res_userinfo_query.result)):
                        wx = reply.res_userinfo_query.result[i]
                        if wx.wxerrcode == 0:
                            subscribe = wx.wxresult.subscribe
                            if subscribe:
                                subscribe = 1
                            else:
                                subscribe = 0
                            openid = wx.wxresult.openid
                            nickname = wx.wxresult.nickname
                            sex = wx.wxresult.sex
                            country = wx.wxresult.country
                            province = wx.wxresult.province
                            city = wx.wxresult.city
                            avatar_uuid = wx.wxresult.avatar_uuid
                            remark = wx.wxresult.remark

                            try :
                                if rediscustdb.exists(openid) :
                                    sql = ("update sr_cust_customer set nickname = \"%s\",fullname = \"%s\",reverse_fullname = reverse(\"%s\"),photo=\"%s\" where openid = \"%s\"" % (nickname,nickname,nickname,avatar_uuid.encode('utf-8'),openid))
                                    cursor.execute(sql)
                                    mydb.commit()
                                    oldinfo = json.loads(rediscustdb.get(openid),strict=False);
                                    rediscustdb.delete(openid)
                                    print(oldinfo)
                                    last_custid = oldinfo["customerid"]
                                    createdtime = oldinfo["createdtime"].encode('utf-8')
                                    custinfonew = '{"customerid":'+str(last_custid)+',"orgid":"'+org_id+'","isattention":'+str(subscribe)+',"openid":"'+openid.encode('utf-8')+'","fullname":"'+nickname.encode('utf-8')+'","nickname":"'+nickname.encode('utf-8')+'","gendercode":'+str(sex)+',"countrycode":"'+country.encode('utf-8')+'","provincecode":"'+province.encode('utf-8')+'","citycode":"'+city.encode('utf-8')+'","photo":"'+avatar_uuid.encode('utf-8')+'","remark":"'+remark.encode('utf-8')+'","createdtime":"'+createdtime+'","accountid":"'+account_id+'"}'
                                    rediscustdb.set(openid,custinfonew)
                            #更新redis里的nickname
                                else:
                                    sql = ("INSERT INTO sr_cust_customer (orgid,isattention,openid,accountid,fullname,reverse_fullname,nickname,gendercode,channelcode,statuscode,countrycode,provincecode,citycode,photo,remark,createdtime) VALUES (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",reverse(\"%s\"),\"%s\",%d,1,1,\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",NOW())" % (org_id.encode('utf-8'),subscribe,openid,account_id,nickname,nickname,nickname,sex,country,province,city,avatar_uuid,remark))
                                    print(sql)
                                    cursor.execute(sql)
                                    last_custid = cursor.lastrowid
                                    mydb.commit()
                                    custinfonew = '{"customerid":'+str(last_custid)+',"orgid":"'+org_id+'","isattention":'+str(subscribe)+',"openid":"'+openid.encode('utf-8')+'","fullname":"'+nickname.encode('utf-8')+'","nickname":"'+nickname.encode('utf-8')+'","gendercode":'+str(sex)+',"countrycode":"'+country.encode('utf-8')+'","provincecode":"'+province.encode('utf-8')+'","citycode":"'+city.encode('utf-8')+'","photo":"'+avatar_uuid.encode('utf-8')+'","remark":"'+remark.encode('utf-8')+'","createdtime":"'+datetime.datetime.strftime(utc_now(), "%Y-%m-%d %H:%M:%S")+'","accountid":"'+account_id+'"}'
                                    rediscustdb.set(openid,custinfonew)
                                    typesql = ("insert into sr_cust_type (`custid`,`typecode`,`isdelete`,`createdtime`)	values(%d,1,0,now())"% last_custid)
                                    cursor.execute(typesql)
                                    mydb.commit()
                                    pointsql = ("insert into sr_point_main(custid,currenttotalnum,cumulativenum,expirednum,usednum,modifiedtime) values (%d,0,0,0,0,now());"% last_custid)
                                    cursor.execute(pointsql)
                                    mydb.commit()
                            except Exception as e:
                                print("昵称编码错误"+str(e))
                                continue;
                                raise
                    #tcount = mongo["openidsync"].count({"logid":logid})
                    tcount = 0
                    templen1 = redisdb.llen("openid")
                    for j in range(0, templen1):
                        tempid1 = redisdb.lindex("openid",j)
                        tempopenid1 = redisdb.hgetall(tempid1)
                        temp_logid1 = int(tempopenid1["logid"])
                        if logid == temp_logid1:
                            tcount = tcount + 1
                    print("tcountssss = " + str(tcount))
                    if tcount == 1:
                        print("custinfosync success")
                        updatelogsql = ("update sr_sys_schedule_log set statecode = 2 where id = %d" % logid)
                        cursor.execute(updatelogsql)
                        mydb.commit()
                    redisdb.delete(listid)
                    redisdb.lrem("openid",1,listid)
                else:
                    print("custinfosync errcode"+str(errcode))
                    #updatelogsql = ("update sr_sys_schedule_log set statecode = 3 where id = %d" % logid)
                    #cursor.execute(updatelogsql)
                    #mydb.commit()
            else:   #如果超时，返回None
                #updatelogsql = ("update sr_sys_schedule_log set statecode = 3 where id = %d" % logid)
                #cursor.execute(updatelogsql)
                #mydb.commit()
                print("custinfosync timeout")

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
    # 使用自定义参数运行
    # --beat同时开启beat模式，即运行按计划发送task的实例
    # 应确保全局只有一份同样的beat
    app.worker_main(["worker", "--beat", "--loglevel=debug","-n","custinfosync.%h","-s","./sche-custinfosync"])
