#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import mysql.connector
import random
from kombu import Exchange, Queue
import json
import uuid
import datetime
import time
import pika
import uuid
import cf_wechat_pb2
import threading
import redis
from rpc import MyRpc

mq_ip = "172.16.0.142"
redis_url = '172.16.0.141'
redis_passwd = 'smartac123'
suffix=''
mysql_conf = {
    'host': '172.16.0.141',
    'port': 3306,
    'database': 'smartrewards',
    'user': 'suser',
    'password': 'spasswd',
    'charset':'utf8mb4'
}

amqp_url = "amqp://guest:guest@"+mq_ip+"/"
url = "amqp://guest:guest@"+mq_ip+":5672/"

mydb = None
def connect():
    global mydb
    if mydb:
        return mydb
    mydb = mysql.connector.connect(**mysql_conf)
    return mydb

def ensure_mysql():
    try:
        mydb.ping()
    except:
        mydb = connect()

redisdb = None
def ensure_redis():
    global redisdb
    if redisdb:
        return redisdb

    redisdb = redis.StrictRedis(host=redis_url,port=6379,password=redis_passwd,db=5)  
    return redisdb

rediscustdb = None
def ensure_cust_redis():
    global rediscustdb
    if rediscustdb:
        return rediscustdb

    rediscustdb = redis.StrictRedis(host=redis_url,port=6379,password=redis_passwd,db=1)
    return rediscustdb


exchange = "amq.direct"
routing_key = "cf.wechat.rpc"
custrouting_key = "cf.wechat.custrpc"
#礼券路由键
couponrouting_key = "sr.customer.coupon.rpc"
#积分路由键
pointrouting_key = "sr.point"+suffix
#会话路由键
sessionrouting_key = "sr.job.session.rpc"
#积分送奖赏路由键
tagrewardrouting_key = "sr.rewards"+suffix


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

custrpc = None
def ensure_custrpc():
    global custrpc
    if custrpc:
        return custrpc

    custrpc = MyRpc(url, exchange, custrouting_key)
    cust = threading.Thread(target=custrpc.serve)
    cust.setDaemon(True)
    cust.start()
    return custrpc

couponrpc = None
def ensure_couponrpc():
    global couponrpc
    if couponrpc:
        return couponrpc

    couponrpc = MyRpc(url, exchange, couponrouting_key)
    coupon = threading.Thread(target=couponrpc.serve)
    coupon.setDaemon(True)
    coupon.start()
    return couponrpc

pointrpc = None
def ensure_pointrpc():
    global pointrpc
    if pointrpc:
        return pointrpc

    pointrpc = MyRpc(url, exchange, pointrouting_key)
    point = threading.Thread(target=pointrpc.serve)
    point.setDaemon(True)
    point.start()
    return pointrpc

sessionrpc = None
def ensure_sessionrpc():
    global sessionrpc
    if sessionrpc:
        return sessionrpc

    sessionrpc = MyRpc(url, exchange, sessionrouting_key)
    session = threading.Thread(target=sessionrpc.serve)
    session.setDaemon(True)
    session.start()
    return sessionrpc

#发微信消息
routing_keyali = "cf.wechat.rpc"
#urlali = "amqp://guest:guest@172.16.0.142:5672/"
exchangeali = "amq.direct"


sendmsgrpc = None
def ensure_sendmsgrpc():
    global sendmsgrpc
    if sendmsgrpc:
        return sendmsgrpc

    sendmsgrpc = MyRpc(url, exchangeali, routing_keyali)
    sendmsg = threading.Thread(target=sendmsgrpc.serve)
    sendmsg.setDaemon(True)
    sendmsg.start()
    return sendmsgrpc

#发短信邮件消息
routing_keysmail = "cf.rpc"
smailrpc = None
def ensure_sendsmailrpc():
    global smailrpc
    if smailrpc:
        return smailrpc

    smailrpc = MyRpc(url, exchangeali, routing_keysmail)
    smail = threading.Thread(target=smailrpc.serve)
    smail.setDaemon(True)
    smail.start()
    return smailrpc

#发短信邮件消息
routing_keysmail = "cf.rpc"
smailrpc = None
def ensure_sendsmailrpc():
    global smailrpc
    if smailrpc:
        return smailrpc

    smailrpc = MyRpc(url, exchangeali, routing_keysmail)
    smail = threading.Thread(target=smailrpc.serve)
    smail.setDaemon(True)
    smail.start()
    return smailrpc

#发app消息
routing_keysapp = "cf.app.rpc"
sapprpc = None
def ensure_sendsapprpc():
    global sapprpc
    if sapprpc:
        return sapprpc

    sapprpc = MyRpc(url, exchangeali, routing_keysapp)
    sapp = threading.Thread(target=sapprpc.serve)
    sapp.setDaemon(True)
    sapp.start()
    return sapprpc