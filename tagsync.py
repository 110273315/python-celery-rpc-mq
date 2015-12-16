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

ONCE_CAPACITY = 100

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
    CELERY_IMPORTS = ("findJob","tasks","usercheck","addJob",),
    CELERYBEAT_SCHEDULE={
        'add-every-10-seconds': {
            'task': 'srjob.usertag.dbsync',
            'schedule': datetime.timedelta(seconds=10),
        }
    }
)

diff_time = time.timezone
def utc_now():
    return datetime.datetime.now() + datetime.timedelta(seconds=diff_time)


@app.task(name="srjob.usertag.dbsync")
def dbsync():
    ensure_mongo()
    ensure_mysql()

    cursor = mydb.cursor()

    task_ids = mongo["task"].find({"status": "STARTED"}, {"_id": 1})
    task_ids = map(lambda x: x["_id"], task_ids)

    for task_id in task_ids:
        try:
            upcount = 0
            tags = mongo["dbsync"].find_one({"task._id": task_id})
            tag_id = tags["tagid"]
            while True:
                doc = mongo["dbsync"].find_one_and_delete({"task._id": task_id}, {"_id": 0, "sql": 1})
                if not doc:
                    break

                upcount += 1

                sql = doc["sql"]

                cursor.execute(sql)

                if upcount % ONCE_CAPACITY == 0:
                    updatesql = ("UPDATE sr_tag_tag SET taghotcount = taghotcount + %d where id = \"%s\"" % (upcount,tag_id))
                    cursor.execute(updatesql)
                    mydb.commit()

            if upcount % ONCE_CAPACITY:
                updatesql = ("UPDATE sr_tag_tag SET taghotcount = taghotcount + %d where id = \"%s\"" % (upcount,tag_id))
                cursor.execute(updatesql)
                mydb.commit()

            if not upcount:
                break

            doc = mongo["task"].find_one_and_update({"_id": task_id, "status": "STARTED", "downcount": {"$exists": True}},
                                                    {"$inc": {"downcount": (0 - upcount)}},
                                                    {"_id": 0, "downcount": 1},
                                                    return_document=pymongo.ReturnDocument.AFTER)
            if doc and doc["downcount"] == 0:
                mongo["task"].update_one({"_id": task_id, "status": "STARTED"},
                                         {"$set": {"status": "SUCCESS", "end_time": utc_now()}})
        except Exception as e:
            mongo["task"].find_one_and_update({"_id": task_id},
                                              {'$set': {"status": "FAILURE", "error": str(e), "end_time": utc_now()}})



if __name__ == "__main__":
    # 使用sys.argv参数运行
    # app.worker_main()

    # 使用自定义参数运行
    # --beat同时开启beat模式，即运行按计划发送task的实例
    # 应确保全局只有一份同样的beat
    app.worker_main(["worker", "--beat", "--loglevel=debug","--concurrency=10","-n","tagsync.%h"])
