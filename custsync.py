#!/usr/bin/env python2.7
# coding:utf-8
from celery import Celery,platforms
from kombu import Exchange, Queue
import pymongo
import mysql.connector
import json
import uuid
import datetime
import time
import pika
import uuid
import cf_wechat_pb2
import threading

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

url = "amqp://guest:guest@172.16.0.64:5672/"
exchange = "amq.direct"
routing_key = "cf.wechat.rpc"

rpc = None
def ensure_rpc():
    global rpc
    if rpc:
        return rpc

    rpc = MyRpc(url, exchange, routing_key)
    t = threading.Thread(target=rpc.serve)
    t.setDaemon(True)
    t.start()
    return rpc


app = Celery("srjob.custinfo", broker=amqp_url)


platforms.C_FORCE_ROOT = True

app.conf.update(
    CELERY_TRACK_STARTED=True,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_IMPORTS = ("findJob","tagsync","usercheck","addJob","addtask","tasks",)
)



@app.task(queue="custsync")
def custsync():
    #创建守护线程，处理amqp事件
    #程序会等待所有非守护线程结束，才会退出
    #守护线程在程序退出时，自动结束
    ensure_rpc()

    req = cf_wechat_pb2.Message()
    req.header.sender="sendre1"
    req.header.sender_type="type1"
    req.req_userinfo_query.account_id = "testid"
    condition = req.req_userinfo_query.customer_search_condition.add()
    condition.wechat_open_id="123"
    data = req.SerializeToString()

    #第二个参数类型float，单位秒，缺省为None，不超时
    data = rpc.call(data)    #1 seconds timeout
    if data:
        reply = cf_wechat_pb2.Message()
        reply.ParseFromString(data)
        print(reply)
        print(reply.res_userinfo_query.errcode)
    else:   #如果超时，返回None
        print("timeout")


class MyRpc:
    def __init__(self, url, exchange, routing_key=""):
        self.url = url
        self.exchange = exchange
        self.routing_key = routing_key

        self.conn = pika.BlockingConnection(pika.URLParameters(self.url))
        self.channel = self.conn.channel()

        self.queue = self.routing_key + "#" + str(uuid.uuid4())
        self.channel.queue_declare(self.queue, exclusive=True)

        #这里是多线程同步的关键
        #锁和条件变量，用于创建消费者-生产模式
        #受锁保护的字典，用来保存rpc的回应
        self.lock = threading.RLock()
        self.cond = threading.Condition(self.lock)
        self.replies = {}

    def consume_cb(self, ch, method, props, body):
        self.cond.acquire()
        try:
            if props.correlation_id in self.replies:
                self.replies[props.correlation_id] = body

                self.cond.notifyAll()
        finally:
            self.cond.release()

    #阻塞操作，需要创建线程来执行该方法
    def serve(self):
        self.channel.basic_consume(self.consume_cb, self.queue)
        self.channel.start_consuming()

    #线程安全
    def call(self, data, timeout=None):

        uid = str(uuid.uuid4())
        reply = None

        self.lock.acquire()
        try:
            #先将key添加到replies，以便回调函数操作
            self.replies[uid] = None
        finally:
            self.lock.release()

        self.channel.basic_publish(self.exchange,
                                   self.routing_key,
                                   properties=pika.BasicProperties(reply_to=self.queue, correlation_id=uid),
                                   body=data)

        while not reply:
            if timeout:
                starttime = time.time()

            self.cond.acquire()
            self.cond.wait(timeout)

            try:
                reply = self.replies[uid]
                if reply:
                    del self.replies[uid]   #从字典中删除该key
                elif timeout:
                    #如果这次没获取到，timeout减去这次消耗的事件
                    timeout -= (time.time() - starttime)

                    #timeout，跳出，返回
                    if timeout <= 0:
                        del self.replies[uid]   #从字典中删除该key
                        break
            finally:
                self.cond.release()

        return reply


#while not finish:
    #conn.process_data_events()
if __name__ == "__main__":
    # 使用自定义参数运行
    # --beat同时开启beat模式，即运行按计划发送task的实例
    # 应确保全局只有一份同样的beat
    app.worker_main(["worker", "--loglevel=debug","--concurrency=10","-n","custsync.%h","-Qcustsync"])
