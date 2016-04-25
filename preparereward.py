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

app = Celery("srjob.reward", broker=amqp_url)


platforms.C_FORCE_ROOT = True

app.conf.update(
    CELERY_TRACK_STARTED=True,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_IMPORTS = ("addsendapp","preparesendapp","dosendapp","addJob","addreward","addsendmail","addsendmsg","addsendsms","addtask","custinfosync","custsync","doreward","dosendmail","dosendmsg","dosendsms","findJob","preparesendmail","preparesendmsg","preparesendsms","sessionclose","tagsync","tasks","usercheck",),
    CELERYBEAT_SCHEDULE={
        'find-reward-every-10-seconds': {
            'task': 'srjob.reward.find',
            'schedule': datetime.timedelta(seconds=60),
        }
    }
)

diff_time = time.timezone
def utc_now():
    return datetime.datetime.now() + datetime.timedelta(seconds=diff_time)


@app.task(name="srjob.reward.find")
def findreward():
    redisdb = ensure_redis()
    listlen = redisdb.llen("reward")
    for i in range(0, listlen):
        listid = redisdb.lindex("reward",i)
        task = redisdb.hgetall(listid)
        print(task['status'])
        count = 1
        listtemplen = redisdb.llen("reward")
        for j in range(0, listtemplen):
            templistid = redisdb.lindex("reward",j)
            temptask = redisdb.hgetall(templistid)
            if temptask['status'] == 'running' or temptask['status'] == 'ERROR':
                count = count + 1
        if count > 1:
            break
        if task['status'] == 'STARTED' and task['isenable'] == '1' and task['prepare'] == '0':
            task_id = task['_id']
            taskargu = eval(task['arguments'])
            if 'campaignid'  in taskargu.keys():
                campaignid = taskargu['campaignid']
            else:
                campaignid = ''
            if 'esttime' in taskargu.keys():
                esttime = taskargu['esttime']
            else:
                esttime = ''
            if 'pointnum' in taskargu.keys():
                pointnum = taskargu["pointnum"]
            else:
                pointnum = ''
            if 'sendtype' in taskargu.keys():
                sendtype = taskargu["sendtype"]
            else:
                sendtype = ''
            if 'couponid' in taskargu.keys():
                couponid = taskargu["couponid"]
            else:
                couponid = ''
            if 'pointexdate' in taskargu.keys():
                pointexdate = taskargu["pointexdate"]
            else:
                pointexdate = ''
            customer = json.loads(taskargu['customer'])
            print(customer)
            campaignid = int(taskargu["campaignid"])
            if datetime.datetime.strptime(esttime, "%Y-%m-%d %H:%M:%S") < (datetime.datetime.now() + datetime.timedelta(seconds=1)):
                redisdb.hset(listid,'status','running')
                try:
                    # 查询sql语句
                    mydb = connect()
                    ensure_mysql()
                    sql = "SELECT cust.id as id,cust.fullname as fullname FROM sr_cust_customer cust "
                    cursor = mydb.cursor()
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

                    cursor.execute(sql)

                    # 创建子任务
                    bulk = redisdb.pipeline()
                    count = 0
                    activetime = datetime.datetime.strptime(esttime, "%Y-%m-%d %H:%M:%S")
                    rows = cursor.fetchall()
        
                    for row in rows:
                        #row = cursor.fetchone()
                        #if not row:
                            #break
            
                        userid = row[0]
                        username = row[1]
                        rewardid = str(uuid.uuid4())

                        bulk.hmset("rewardsync:"+rewardid,{
                            "username":username,
                            "campaignid":campaignid,
                            "pointnum": pointnum,
                            "sendtype":sendtype,
                            "couponid":couponid,
                            "pointexdate":pointexdate,
                            "userid":userid,
                            "task_id":task_id,
                            "activetime":activetime,
                            "rewardid":rewardid,
                            "status":1
                        })
                        
                        bulk.lpush("rewardsync","rewardsync:"+rewardid)
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
    app.worker_main(["worker", "--beat", "--loglevel=debug","-n","preparereward.%h","-s","./sche-preparereward"])