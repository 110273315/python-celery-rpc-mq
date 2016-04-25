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
ONCE_PRENUM = 10000

app = Celery("srjob.sendmsg", broker=amqp_url)


platforms.C_FORCE_ROOT = True

app.conf.update(
    CELERY_TRACK_STARTED=True,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_IMPORTS = ("addsendapp","preparesendapp","dosendapp","addJob","addreward","addsendmail","addsendmsg","addsendsms","addtask","custinfosync","custsync","doreward","dosendmail","dosendmsg","dosendsms","findJob","preparereward","preparesendmail","preparesendsms","sessionclose","tagsync","tasks","usercheck",),
    CELERYBEAT_SCHEDULE={
        'find-reward-every-10-seconds': {
            'task': 'srjob.sendmsg.find',
            'schedule': datetime.timedelta(seconds=60),
        }
    }
)

diff_time = time.timezone
def utc_now():
    return datetime.datetime.now() + datetime.timedelta(seconds=diff_time)


@app.task(name="srjob.sendmsg.find")
def findsendmsg():
    redisdb = ensure_redis()
    listlen = redisdb.llen("sendmsg")
    for i in range(0, listlen):
        listid = redisdb.lindex("sendmsg",i)
        task = redisdb.hgetall(listid)
        count = 1
        listtemplen = redisdb.llen("sendmsg")
        for j in range(0, listtemplen):
            templistid = redisdb.lindex("sendmsg",j)
            temptask = redisdb.hgetall(templistid)
            if temptask['status'] == 'running':
                count = count + 1
        if count > 1:
            break
        if task['status'] == 'STARTED' and task['isenable'] == '1':
            task_id = task['_id']
            taskargu = eval(task['arguments'])
            esttime = task["esttime"]
            campaignid = int(taskargu["campaignid"])
            wechatid = int(taskargu['wechatid'])
            customer = json.loads(taskargu['customer'])
            if datetime.datetime.strptime(esttime, "%Y-%m-%d %H:%M:%S") < (datetime.datetime.now() + datetime.timedelta(seconds=1)):
                try:
                    redisdb.hset(listid,'status','running')
                    mydb = connect()
                    ensure_mysql()
                    cursor = mydb.cursor()
                    # 查询sql语句
                    sql = "SELECT cust.id,cust.openid FROM sr_cust_customer cust "
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

                    wechatsql = ("SELECT id,campaignid,title,sendaccount,wechattype,sortno,author,abstract,content,linkurl,fileid,isenabled from sr_campaign_wechat where id= %d" % (wechatid))
                    print(wechatsql)
                    cursor.execute(wechatsql)
                    wechat = cursor.fetchall()
                    wechatrow = wechat[0]
                    if not wechatrow:
                        break
                    print(wechatrow)
                    wechattype = wechatrow[4]
                    if wechattype == 3:
                        content = wechatrow[8]
                    elif wechattype == 4:
                        voicesql = ("SELECT fileid from sr_weiapp_resource where id = %d" % (int(wechatrow[8])))
                        cursor.execute(voicesql)
                        voicerow = cursor.fetchone()
                        if not voicerow:
                            break
                        content = voicerow[0]
                    elif wechattype == 5:
                        videosql = ("SELECT fileid,filename from sr_weiapp_resource where id = %d" % (int(wechatrow[8])))
                        cursor.execute(videosql)
                        videorow = cursor.fetchone()
                        if not videorow:
                            break
                        content = videorow[0]+"@filename@"+videorow[1]
                    else :
                        contentsql = ("SELECT jsonfileid from sr_weiapp_reply_content where id = %d" % (int(wechatrow[8])))
                        cursor.execute(contentsql)
                        contentrow = cursor.fetchone()
                        if not contentrow:
                            break
                        content = contentrow[0]
                    print(content)
                    wechatid = wechatrow[0]
                    campaignid = wechatrow[1]
                    title = wechatrow[2]
                    sendaccount = wechatrow[3]
                    sortno = wechatrow[5]
                    author = wechatrow[6]
                    abstract = wechatrow[7]

                    linkurl = wechatrow[9]
                    fileid = wechatrow[10]
                    isenabled = wechatrow[11]
                    cursor.execute(sql)

                    count = 0

                    times = 0
                    openids = ""
                    while True:
                        row = cursor.fetchone()
                        if not row:
                            break
                        print(esttime)
                        #esttime = datetime.datetime.strftime(esttime, "%Y-%m-%d %H:%M:%S")
                        id = row[0]
                        openid = row[1]

                        sendmsgid = str(uuid.uuid4())
                        if openid:
                            openids=openids+openid.encode('utf-8')+","
                            count += 1
                            if count % ONCE_PRENUM == 0:
                                times += 1
                                redisdb.hmset("sendmsgsync:"+sendmsgid,{
                                    "openid":openids,
                                    "custid":id,
                                    "sendmsgid":sendmsgid,
                                    "campaignid":campaignid,
                                    "sendaccount":sendaccount,
                                    "wechattype":wechattype,
                                    "content":content,
                                    "task_id":task_id,
                                    "activetime":esttime,
                                    "status":1
                                })
                                redisdb.lpush("sendmsgsync","sendmsgsync:"+sendmsgid)
                                esttime = datetime.datetime.strptime(esttime, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(minutes=30)
                                esttime = datetime.datetime.strftime(esttime, "%Y-%m-%d %H:%M:%S")
                                openids = ""


                    if count % ONCE_PRENUM:
                        times += 1
                        redisdb.hmset("sendmsgsync:"+sendmsgid,{
                            "openid":openids,
                            "custid":id,
                            "sendmsgid":sendmsgid,
                            "campaignid":campaignid,
                            "sendaccount":sendaccount,
                            "wechattype":wechattype,
                            "content":content,
                            "task_id":task_id,
                            "activetime":esttime,
                            "status":1
                        })
                        redisdb.lpush("sendmsgsync","sendmsgsync:"+sendmsgid)

                    redisdb.hmset(listid,{"isenable":0,"prepare":1,"queried": times, "downcount": times})

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
    app.worker_main(["worker", "--beat", "--loglevel=debug","-n","preparesendmsg.%h","-s","./sche-preparesendmsg"])