#!/usr/bin/env python2.7
# coding:utf-8

from kombu import Exchange, Queue
import json
import uuid
import datetime
import time
import pika
import uuid
import threading


class MyRpc:
    def __init__(self, url, exchange, routing_key=""):
        self.url = url
        self.exchange = exchange
        self.routing_key = routing_key
        self.conn = pika.BlockingConnection(pika.URLParameters(self.url))
        self.channel = self.conn.channel()
        #self.channel.exchange_declare(durable=False,exchange=self.exchange,type='topic',)
        self.queue = self.routing_key + "#" + str(uuid.uuid4())
        self.channel.queue_declare(self.queue, exclusive=True,auto_delete=True)
        self.channel.queue_bind(self.queue, self.exchange, self.queue)

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
                ch.basic_ack(method.delivery_tag)
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



