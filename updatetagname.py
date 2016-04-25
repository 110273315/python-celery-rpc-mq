#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from celery import task
from kombu import Exchange, Queue
from config import *
import mysql.connector
import json
import uuid
import datetime
import time
import sr_job_task_pb2


conn = pika.BlockingConnection(pika.ConnectionParameters(mq_ip))
channel = conn.channel()

exchange = "amq.direct"
channel.exchange_declare(exchange,durable='false')

routing_key = "sr.job.updatetag"

queue = "sr.job.updatetag#" + str(uuid.uuid4())
channel.queue_declare(queue, auto_delete=True)
channel.queue_bind(queue, exchange, routing_key)

diff_time = time.timezone
def utc_now():
    return datetime.datetime.now() + datetime.timedelta(seconds=diff_time)

def cb(ch, method, props, body):
    req = sr_job_task_pb2.Message()
    req.ParseFromString(body)
    task_id = req.req_tag_update.id
    tagname = req.req_tag_update.tagname
    redisdb = ensure_redis()
    mydb = connect()
    ensure_mysql()
    reply = sr_job_task_pb2.Message()
    try:
        # 查询sql语句
        sql = ("UPDATE sr_sys_schedule_task SET taskname=\"%s\" where id = %d" % (tagname,task_id))
        cursor = mydb.cursor()
        cursor.execute(sql)
        mydb.commit()
        #cursor.close()
        #mydb.close()
        redisdb.hset("job:"+str(task_id),"taskname",tagname)

        reply.header.sender="res_tag_update"
        reply.header.sender_type="type1"
        reply.res_tag_update.errcode = 0
        reply.res_tag_update.errmsg = "success"

    except Exception as e:
        # 更新task状态
        reply.header.sender="res_tag_update"
        reply.header.sender_type="type1"
        reply.res_tag_update.errcode = -1
        reply.res_tag_update.errmsg = "failure"

    buff = reply.SerializeToString()

    ch.basic_publish(exchange="amq.direct",
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=buff)


channel.basic_consume(cb, queue, no_ack=True)
channel.start_consuming()

