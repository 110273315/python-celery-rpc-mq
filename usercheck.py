#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from celery import Celery,platforms
from kombu import Exchange, Queue
import pymongo
import mysql.connector
import json
import uuid
import datetime
import time

ONCE_CAPACITY = 5000

amqp_url = "amqp://guest:guest@172.16.0.64/"
mongo_url = "mongodb://172.16.0.64/srjob"
mysql_conf = {
    'host': '172.16.0.176',
    'port': 3306,
    'database': 'smartrewardsdev_30',
    'user': 'srdev',
    'password': 'sr_dev1124'
}

mongo = None
def ensure_mongo():
    global mongo
    if mongo:
        return mongo

    mongo = pymongo.MongoClient(mongo_url);
    mongo = mongo[mongo_url.split("/")[-1]]
    return mongo


mydb = None
def ensure_mysql():
    global mydb
    if mydb:
        return mydb

    mydb = mysql.connector.connect(**mysql_conf);
    return mydb


app = Celery("srjob.usertag", broker=amqp_url)


platforms.C_FORCE_ROOT = True

app.conf.update(
    CELERY_TRACK_STARTED=True,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_IMPORTS = ("findJob","tasks","addtask","addJob",)
)

diff_time = time.timezone
def utc_now():
    return datetime.datetime.now() + datetime.timedelta(seconds=diff_time)



@app.task(queue="usercheck")
def usercheck(parent_id, userid, tagid):
    ensure_mongo()
    ensure_mysql()


    try:
        cursor = mydb.cursor()
        
        upcount = 0     #总任务倒计数
        sqlcount = 0    #sql数量
        empty = False   #临时集合已空
        bulk = mongo["dbsync"].initialize_unordered_bulk_op()        
        
        #usertag的退出策略有两种
        #第一种是直到集合内数据全处理完，这很可能会阻塞整个任务队列
        #第二种是每个suertag任务处理掉一定量的数据，就退出。鉴于usertag是个费时的操作，这对整个任务队列的通畅意义也不大
        #如果采用第二种，须注意：一、创建合适数量的usertag任务，不要留下尾巴数据；二、注意删除临时集合的时机
        #while True:
        for x in range(ONCE_CAPACITY):
            doc = mongo["task_"+str(parent_id)].find_one_and_delete({})
            if not doc:
                empty = True
                break
            
            userid = doc["userid"]
            if str(userid).isdigit():
                userid = int(str(userid).encode('utf-8'))

            # 查询user是否已经有该tag
            sql = "SELECT * FROM sr_tag_cust WHERE tagid = %d AND custid = %d" % (tagid,userid)
            cursor.execute(sql)
            if len(cursor.fetchall()) == 0:
                # 创建sql，保存到mongo，等dbsync执行
                sql = "INSERT INTO sr_tag_cust VALUES(NULL,%d, %d, %d)" % (userid, tagid,parent_id)
                bulk.insert({
                    "task": {
                        "_id": parent_id,
                        "name": "srjob.usertag.add"
                    },
                    "sql": sql,
					"tagid":tagid
                })
                
                sqlcount += 1
                if sqlcount % ONCE_CAPACITY == 0:
                    bulk.execute()
                    bulk = mongo["dbsync"].initialize_unordered_bulk_op()
            else:
                #减少倒计数
                upcount += 1

        #最后一批sql
        if sqlcount % ONCE_CAPACITY:
            bulk.execute()

        #删除临时集合
        #find_one_and_delete返回None，表明集合已为空
        #测试表明，删除不存在的集合无异常
        if empty:
            mongo["task_"+str(parent_id)].drop()

        #增加upcount
        if upcount:
            doc = mongo["task"].find_one_and_update({"_id": parent_id, "status": "STARTED", "downcount": {"$exists": True}},
                                                    {"$inc": {"downcount": (0 - upcount)}},
                                                    {"_id": 0, "downcount": 1},
                                                    return_document=pymongo.ReturnDocument.AFTER)
            if doc and doc["downcount"] == 0:
                mongo["task"].update_one({"_id": parent_id, "status": "STARTED"},
                                         {"$set": {"status": "SUCCESS", "end_time": utc_now()}})

    except Exception as e:
        mongo["task"].update_one({"_id": parent_id},
                                 {"$set": {"status": "FAILURE", "error": str(e), "end_time": utc_now()}})
        raise


if __name__ == "__main__":
    # 使用sys.argv参数运行
    # app.worker_main()

    # 使用自定义参数运行
    # --beat同时开启beat模式，即运行按计划发送task的实例
    # 应确保全局只有一份同样的beat
    app.worker_main(["worker", "--beat", "--loglevel=debug","-Qusercheck","--concurrency=10","-n","usercheck.%h"])
