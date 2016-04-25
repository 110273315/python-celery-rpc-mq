#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from celery import Celery,platforms
from kombu import Exchange, Queue
from celery import task
from config import *
import mysql.connector
import json
import uuid
import datetime
import time

ONCE_CAPACITY = 10000
ONCE_PRENUM = 50000

app = Celery("srjob.sendmail", broker=amqp_url)


platforms.C_FORCE_ROOT = True

app.conf.update(
    CELERY_TRACK_STARTED=True,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_IMPORTS = ("addsendapp","preparesendapp","dosendapp","addJob","addreward","addsendmail","addsendmsg","addsendsms","addtask","custinfosync","custsync","doreward","dosendmail","dosendmsg","dosendsms","findJob","preparereward","preparesendmsg","preparesendsms","sessionclose","tagsync","tasks","usercheck",),
    CELERYBEAT_SCHEDULE={
        'find-reward-every-10-seconds': {
            'task': 'srjob.sendmail.find',
            'schedule': datetime.timedelta(seconds=60),
        }
    }
)

diff_time = time.timezone
def utc_now():
    return datetime.datetime.now() + datetime.timedelta(seconds=diff_time)


@app.task(name="srjob.sendmail.find")
def findsendmail():
    redisdb = ensure_redis()

    listlen = redisdb.llen("sendmail")
    for i in range(0, listlen):
        listid = redisdb.lindex("sendmail",i)
        task = redisdb.hgetall(listid)
        print(task['status'])
        count = 1
        listtemplen = redisdb.llen("sendmail")
        for j in range(0, listtemplen):
            templistid = redisdb.lindex("sendmail",j)
            temptask = redisdb.hgetall(templistid)
            if temptask['status'] == 'running' or temptask['status'] == 'ERROR':
                count = count + 1
        if count > 1:
            break
        if task['status'] == 'STARTED' and task['isenable'] == '1' and task['prepare'] == '0':
            task_id = task['_id']
            taskargu = eval(task['arguments'])
            esttime = task["esttime"]
            mailid = taskargu['mailid']
            campaignid = int(taskargu["campaignid"])
            customer = json.loads(taskargu['customer'])
            if datetime.datetime.strptime(esttime, "%Y-%m-%d %H:%M:%S") < (datetime.datetime.now() + datetime.timedelta(seconds=1)):
                redisdb.hset(listid,'status','running')
                try:
                    mydb = connect()
                    ensure_mysql()
                    # 执行sql查询
                    cursor = mydb.cursor()
                    # 查询sql语句
                    sql = "SELECT cust.id,cust.emailaddress,cust.fullname FROM sr_cust_customer cust "
                    campsql = ("SELECT filtersql from sr_campaign_filterrule where campaignid = %d" % campaignid)
                    cursor.execute(campsql)
                    camprow = cursor.fetchone()
                    if not camprow:
                        break
                    wheresql = ("SELECT FROM_BASE64(\"%s\") as condit" % camprow[0])
                    cursor.execute(wheresql)
                    whererow = cursor.fetchone()
                    if not whererow:
                        break
                    conditions = []
                    conditions.append("WHERE 1 = 1")
                    conditions.append(" AND %s" % whererow[0])
                    sql = sql + ''.join(conditions)
                    print(sql)



                    #查询消息相关条件

                    mailsql = ("SELECT campaignid,title,sendaccount,content from sr_campaign_email where id= %d" % (mailid))

                    cursor.execute(mailsql)
                    mailrow = cursor.fetchone()
                    if not mailrow:
                        break
                    campaignid = mailrow[0]
                    title = mailrow[1]
                    sendaccount = mailrow[2]
                    content = mailrow[3]


                    cursor.execute(sql)

                    # 创建子任务
                    bulk = redisdb.pipeline()
                    count = 0
                    activetime = datetime.datetime.strptime(esttime, "%Y-%m-%d %H:%M:%S")
        
                    while True:
                        row = cursor.fetchone()
                        if not row:
                            break

                        id = row[0]
                        emailaddress = row[1]
                        custname = row[2]
                        sendmailid = str(uuid.uuid4())
                        print(emailaddress)
                        bulk.hmset("sendmailsync:"+sendmailid,{
                            "sendmailid":sendmailid,
                            "emailaddress":emailaddress,
                            "custid":id,
                            "custname":custname,
                            "campaignid":campaignid,
                            "sendaccount":sendaccount,
                            "content":title + "@html@" + content,
                            "task_id":task_id,
                            "activetime":activetime,
                            "status":1
                        })
                        bulk.lpush("sendmailsync","sendmailsync:"+sendmailid)
                        count += 1
                        if count % ONCE_CAPACITY == 0:
                            bulk.execute()

                    if count % ONCE_CAPACITY:
                        bulk.execute()

                    redisdb.hmset(listid,{"isenable":1,"prepare":1,"queried":count,"downcount":count})

                except Exception as e:
                    print(str(e))
                    redisdb.hmset(listid,{"status":"STARTED","error":str(e)})
                    raise



if __name__ == "__main__":
    # 使用sys.argv参数运行
    # app.worker_main()

    # 使用自定义参数运行
    # --beat同时开启beat模式，即运行按计划发送task的实例
    # 应确保全局只有一份同样的beat
    app.worker_main(["worker", "--beat", "--loglevel=debug","-n","preparesendmail.%h","-s","./sche-preparesendmail"])