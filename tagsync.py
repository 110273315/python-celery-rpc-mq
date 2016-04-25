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
import sr_reward_pb2



ONCE_CAPACITY = 5000
app = Celery("srjob.usertag", broker=amqp_url)


platforms.C_FORCE_ROOT = True

app.conf.update(
    CELERY_TRACK_STARTED=True,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_IMPORTS = ("addsendapp","preparesendapp","dosendapp","addJob","addreward","addsendmail","addsendmsg","addsendsms","addtask","custinfosync","custsync","doreward","dosendmail","dosendmsg","dosendsms","findJob","preparereward","preparesendmail","preparesendmsg","preparesendsms","sessionclose","tasks","usercheck",),
    CELERYBEAT_SCHEDULE={
        'add-every-10-seconds': {
            'task': 'srjob.usertag.dbsync',
            'schedule': datetime.timedelta(seconds=60),
        }
    }
)

diff_time = time.timezone
def utc_now():
    return datetime.datetime.now() + datetime.timedelta(seconds=diff_time)


@app.task(name="srjob.usertag.dbsync")
def dbsync():
    redisdb = ensure_redis()
    mydb = connect()
    ensure_mysql()

    cursor = mydb.cursor()
    listlen = redisdb.llen("task")
    for i in range(0, listlen):
        listid = redisdb.lindex("task",i)
        logtask = redisdb.hgetall(listid)
        print(logtask['status'])
        if logtask['status'] == 'STARTED' and logtask['isenable'] == '1' and logtask['prepare'] == '1':
            redisdb.hset(listid,'isenable',0)
            task_id = logtask['_id']
            synclistlen = redisdb.llen("dbsync")
            print("synclistlen="+str(synclistlen))
            for i in range(synclistlen-1,-1,-1):
                print(i)
                synclistid = redisdb.lindex("dbsync",i)
                tagsync = redisdb.hgetall(synclistid)
                if tagsync['_id']==task_id:
                    tag_id = tagsync["tagid"]
                    sql = tagsync["sql"]
                    custids = tagsync["custids"]
                    upcount = int(tagsync["count"])
                    tagcount = int(tagsync["tagcount"])
                    if "logid" in tagsync.keys():
                        logid = tagsync["logid"]
                    else:
                        logid = 0
                    try:
                        if sql != "INSERT INTO sr_tag_cust VALUES":
                            cursor.execute(sql)
                        updatesql = ("UPDATE sr_tag_tag SET taghotcount = taghotcount + %d where id = %d" % (tagcount,int(tag_id)))
                        cursor.execute(updatesql)
                        mydb.commit()
                        redisdb.delete(synclistid)
                        redisdb.lrem("dbsync",1,synclistid)
                        redisdb.hincrby("task:"+str(task_id),'downcount',-upcount)
                        print("tagreward=====================")
                        if custids != "None":
                            sendrwd(custids)
                        newsendsms = redisdb.hgetall(listid)
                        if newsendsms and newsendsms["downcount"] == '0':
                            redisdb.hmset("task:"+str(task_id),{"status":"SUCCESS", "end_time":utc_now()})
                            if logid:
                                updatelogsql = ("update sr_sys_schedule_log set statecode = 2 where id = %d" % int(logid))
                                cursor.execute(updatelogsql)
                                mydb.commit()

                    except Exception as e:
                        print("error==="+str(e))
                        redisdb.hmset("task:"+str(task_id),{"status":"FAILURE", "end_time":utc_now(), "error": str(e)})
                        if logid:
                            updatelogsql = ("update sr_sys_schedule_log set statecode = 3 where id = %d" % int(logid))
                            cursor.execute(updatelogsql)
                            mydb.commit()

def sendrwd(custids):
    conn = pika.BlockingConnection(pika.ConnectionParameters(mq_ip))
    channel = conn.channel()
    exchange = "sr.rewards.notify"
    channel.exchange_declare(exchange,durable='true')
    req = sr_reward_pb2.Message()
    req.header.sender="req_tag"
    req.header.sender_type="type1"
    req.req_tag.custid = custids
    req.req_tag.tagtime = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
    print(req)
    buff = req.SerializeToString()
    channel.basic_publish(exchange=exchange,
         routing_key=tagrewardrouting_key,
         body=buff)

    conn.close()




if __name__ == "__main__":
    # 使用sys.argv参数运行
    # app.worker_main()

    # 使用自定义参数运行
    # --beat同时开启beat模式，即运行按计划发送task的实例
    # 应确保全局只有一份同样的beat
    app.worker_main(["worker", "--beat", "--loglevel=debug","-n","tagsync.%h","-s","./sche-tagsync"])
