#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from config import *
from kombu import Exchange, Queue
import mysql.connector
import json
import uuid
import datetime
import time


def initdata():
    redisdb = ensure_redis()

    redisdb.hmset("job:26",{
                "_id" : 26,
                "nexttime" : "2016-02-19 09:27:51",
                "status" : "WAITTED",
                "task" : "custinfosync",
                "isenable" : 1,
                "arguments" : {
                    "week" : 0,
                    "hour" : 10,
                    "nexttime" : "2016-01-7 18:59:59",
                    "isenabled" : 1,
                    "starttime" : "7,18:59:59",
                    "month" : 7,
                    "periodcode" : 3,
                    "createdid" : "1231",
                    "time" : "22:59:59",
                    "tasktypecode" : 4,
                    "taskname" : "同步微信会员",
                    "tagid" : 51920,
                    "minute" : 2
                }
            })
    redisdb.lpush("job","job:26")
    redisdb.hmset("job:27",{
                "_id" : 27,
                "nexttime" : "2016-02-18 10:00:09",
                "status" : "WAITTED",
                "task" : "sessionclose",
                "isenable" : 1,
                "arguments" : {
                    "week" : 0,
                    "hour" : 10,
                    "nexttime" : "2016-01-7 18:59:59",
                    "isenabled" : 1,
                    "starttime" : "7,18:59:59",
                    "month" : 7,
                    "periodcode" : 1,
                    "createdid" : "1231",
                    "time" : "18:59:59",
                    "tasktypecode" : 5,
                    "taskname" : "关闭多客服会话",
                    "tagid" : 51920,
                    "minute" : 2
                }
            })
    redisdb.lpush("job","job:27")
    print("初始化数据完成.")



if __name__ == "__main__":
    initdata()

