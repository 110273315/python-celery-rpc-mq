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

ONCE_CAPACITY = 200

app = Celery("srjob.usertag", broker=amqp_url)

platforms.C_FORCE_ROOT = True

app.conf.update(
    CELERY_TRACK_STARTED=True,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_IMPORTS = ("addsendapp","preparesendapp","dosendapp","addJob","addreward","addsendmail","addsendmsg","addsendsms","addtask","custinfosync","custsync","doreward","dosendmail","dosendmsg","dosendsms","findJob","preparereward","preparesendmail","preparesendmsg","preparesendsms","sessionclose","tagsync","tasks",)
)

diff_time = time.timezone
def utc_now():
    return datetime.datetime.now() + datetime.timedelta(seconds=diff_time)



@app.task(queue="usercheck")
def usercheck(parent_id, userid, tagid,logid):
    print("usercheckusercheckusercheckusercheck")
    redisdb = ensure_redis()
    mydb = connect()
    ensure_mysql()

    try:
        cursor = mydb.cursor()
        
        dropcount = 0     #已打过数量
        sqlcount = 0    #sql数量
        tagcount = 0

        task = redisdb.hgetall("task:"+str(parent_id))
        querycount = task["queried"]
        listlen = redisdb.llen("task_"+str(parent_id))
        vallist = []
        custids = []
        for i in range(0, listlen):
            userid = redisdb.lindex("task_"+str(parent_id),i)
            if str(userid).isdigit():
                userid = int(str(userid).encode('utf-8'))

            # 查询user是否已经有该tag
            sql = "SELECT * FROM sr_tag_cust WHERE tagid = %d AND custid = %d" % (tagid,userid)
            cursor.execute(sql)
            sqlcount += 1
            if len(cursor.fetchall()) == 0:
                tagcount += 1
                # 创建sql，保存到mongo，等dbsync执行
                custids.append(str(userid))
                vallist.append("("+str(tagid)+","+str(userid)+","+str(parent_id)+")")
                if sqlcount % ONCE_CAPACITY == 0: 
                    val= ','.join(vallist)
                    custidstring=','.join(custids)
                    sql = "INSERT INTO sr_tag_cust VALUES"+val
                    print(sql)
                    tempid = str(uuid.uuid4())
                    if logid:
                        redisdb.hmset("dbsync:"+tempid,{
                            "_id": parent_id,
                            "logid": logid,
                            "custids": custidstring,
                            "sql": sql,
                            "count": sqlcount,
                            "tagcount":tagcount,
					        "tagid":tagid
                        })
                    else:
                        redisdb.hmset("dbsync:"+tempid,{
                            "_id": parent_id,
                            "sql": sql,
                            "custids": custidstring,
                            "count": sqlcount,
                            "tagcount":tagcount,
					        "tagid":tagid
                        })
                    redisdb.lpush("dbsync","dbsync:"+tempid)
                    vallist = []
                    custids = []
                    sqlcount = 0
                    tagcount = 0
                #sqlcount += 1
            else:
                dropcount += 1

        #if int(querycount) == dropcount:
            #cursor = mydb.cursor()
            #updatelogsql = ("update sr_sys_schedule_log set statecode = 2 where id = %d" % int(logid))
            #cursor.execute(updatelogsql)
            #mydb.commit()
            #redisdb.hmset("task:"+str(parent_id),{"status":"SUCCESS", "end_time":utc_now()})
        #else:
        #最后一批sql
        if sqlcount % ONCE_CAPACITY:
            val= ','.join(vallist)
            custidstring=','.join(custids)
            sql = "INSERT INTO sr_tag_cust VALUES"+val
            print(sql)
            tempid = str(uuid.uuid4())
            if logid:
                redisdb.hmset("dbsync:"+tempid,{
                    "_id": parent_id,
                    "logid": logid,
                    "sql": sql,
                    "custids": custidstring,
                    "count": sqlcount,
                    "tagcount":tagcount,
                    "tagid":tagid
                })
            else:
                redisdb.hmset("dbsync:"+tempid,{
                    "_id": parent_id,
                    "sql": sql,
                    "custids": custidstring,
                    "count": sqlcount,
                    "tagcount":tagcount,
                    "tagid":tagid
                })
            redisdb.lpush("dbsync","dbsync:"+tempid)
        redisdb.delete("task_"+str(parent_id))
        redisdb.hset("task:"+str(parent_id),'prepare',1)


    except Exception as e:
        redisdb.hmset("task:"+str(parent_id),{"status":"FAILURE", "end_time":utc_now(), "error": str(e)})
        raise


if __name__ == "__main__":
    # 使用sys.argv参数运行
    # app.worker_main()

    # 使用自定义参数运行
    # --beat同时开启beat模式，即运行按计划发送task的实例
    # 应确保全局只有一份同样的beat
    app.worker_main(["worker", "--loglevel=debug","-Qusercheck","-n","usercheck.%h"])
