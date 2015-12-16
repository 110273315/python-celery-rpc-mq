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
    CELERY_IMPORTS = ("findJob","tagsync","usercheck","addJob",)
)

diff_time = time.timezone
def utc_now():
    return datetime.datetime.now() + datetime.timedelta(seconds=diff_time)


@app.task(queue="addtask")
def add(task):
    ensure_mongo()
    ensure_mysql()

    task = task
    tagid = task["tagid"]
    #task_id = task["taskid"]
    customer = task["customer"]
    inserttask = ("INSERT INTO sr_tag_task(id,orgid,historytype,historysource,tagid,isusetagsql,custlist,tagsql,isactivities,createrid,createdtime) values (null,NULL,2,1,\"%s\",1,NULL,\"%s\",0,NULL,NOW());" % (tagid,_decode_dict(customer)))
    #保存到mysql
    cursor = mydb.cursor()
    cursor.execute(inserttask)
    task_id = cursor.lastrowid
    mydb.commit()

    # 保存task状态
    # taskmeta的数据不可定制，所以来份自己的
    mongo["task"].insert({
        "_id": task_id,
        "task": "srjob.usertag.add",
        "arguments": task,
        "begin_time": utc_now(),
        "status": "STARTED"
    })

    try:
        # 查询sql语句
        sql = "SELECT sc.id FROM sr_cust_customer sc LEFT JOIN sr_cust_trade st on sc.id = st.custid LEFT JOIN sr_tag_cust stc on sc.id = stc.custid "
        conditions = []
        conditions.append("WHERE 1 = 1")
        if "mobile" in customer.keys():
            conditions.append(" AND sc.mobile = \"%s\"" % customer["mobile"])
        if "shopid" in customer.keys():
            conditions.append(" AND sc.orgid = \"%s\"" % customer["shopid"])
        if "sexcode" in customer.keys():
            conditions.append(" AND sc.gendercode = %d" % customer["sexcode"])
        if "typecode" in customer.keys():
            conditions.append(" AND sc.typecode = %d" % customer["typecode"])
        if "sourcecode" in customer.keys():
            conditions.append(" AND sc.channelcode = %d" % customer["sourcecode"])
        if "frequencymin" in customer.keys():
            conditions.append(" AND sc.tradetimes >= %d" % customer["frequencymin"])
        if "frequencymax" in customer.keys():
            conditions.append(" AND sc.tradetimes <= %d" % customer["frequencymax"])
        if "amountmin" in customer.keys():
            conditions.append(" AND sc.totaltradeamount <= %d" % customer["amountmin"])
        if "amountmax" in customer.keys():
            conditions.append(" AND sc.totaltradeamount <= %d" % customer["amountmax"])
        if "idtags" in customer.keys():
            conditions.append(" AND stc.tagid IN (%s)" % customer["idtags"])
        if "agemin" in customer.keys():
            conditions.append(" AND (DATE_FORMAT( FROM_DAYS( TO_DAYS( NOW( ) ) – TO_DAYS( sc.birthday ) ) , \‘%Y\’ ) +0) >= %d" % customer["agemin"])
        if "agemax" in customer.keys():
            conditions.append(" AND (DATE_FORMAT( FROM_DAYS( TO_DAYS( NOW( ) ) – TO_DAYS( sc.birthday ) ) , \‘%Y\’ ) +0) <= %d" % customer["agemax"])
        if "createdstarttime" in customer.keys():
            conditions.append(" AND sc.createdtime >= \"%s\"" % customer["createdstarttime"])
        if "createdendtime" in customer.keys():
            conditions.append(" AND sc.createdtime <= \"%s\"" % customer["createdendtime"])
        if "tradestartdate" in customer.keys():
            conditions.append(" AND st.createdtime >= \"%s\"" % customer["tradestartdate"])
        if "tradeenddate" in customer.keys():
            conditions.append(" AND st.createdtime <= \"%s\"" % customer["tradeenddate"])
        sql = sql + ''.join(conditions)
        print(sql)

        # 执行sql查询
        #cursor = mydb.cursor()
        cursor.execute(sql)

        # 创建子任务
        bulk = mongo["task_"+str(task_id)].initialize_unordered_bulk_op()
        count = 0
        
        while True:
            row = cursor.fetchone()
            if not row:
                break
            
            userid = row[0]
            
            bulk.insert({
                "userid": userid
            })
            
            count += 1
            if count % ONCE_CAPACITY == 0:
                bulk.execute()
                bulk = mongo["task_"+str(task_id)].initialize_unordered_bulk_op()
            
        if count % ONCE_CAPACITY:
            bulk.execute()

        # 倒计数
        # 一并加上查询到的数量
        mongo["task"].update_one({"_id": task_id}, {"$set": {"queried": cursor.rowcount, "downcount": cursor.rowcount}})
        #创建子任务
        #最后创建子任务，易于处理downcount
        for x in range((cursor.rowcount + ONCE_CAPACITY -1) /ONCE_CAPACITY):
            app.send_task('srjob.usertag.usercheck',args=[task_id, userid, tagid],queue='usercheck')
    except Exception as e:
        # 更新task状态
        mongo["task"].update_one({"_id": task_id},
                                 {"$set": {"status": "FAILURE", "error": str(e), "end_time": utc_now()}})
        raise

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


if __name__ == "__main__":
    # 使用sys.argv参数运行
    # app.worker_main()

    # 使用自定义参数运行
    # --beat同时开启beat模式，即运行按计划发送task的实例
    # 应确保全局只有一份同样的beat
    app.worker_main(["worker", "--beat", "--loglevel=debug","--concurrency=10","-n","autoaddtask.%h","-Qaddtask"])
