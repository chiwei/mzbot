#!/usr/bin/env python3
# coding: UTF-8

import json
import random
import re
import datetime
import time
from validator import validator
from validator import validatorBarcode

from apscheduler.schedulers.background import BackgroundScheduler
from cqsdk import CQBot, CQAt, RE_CQ_SPECIAL, CQImage, RcvdPrivateMessage, \
    RcvdGroupMessage, SendGroupMessage, GroupMemberIncrease,  GroupBan
from collections import deque
from utils import match, reply
from db.queryOrgs import queryOrgByCode
from db.queryRegions import queryRegionByCode

qqbot = CQBot(11235)
scheduler = BackgroundScheduler(
    timezone='Asia/Tokyo',
    job_defaults={'misfire_grace_time': 60},
    )

################  Restriction
MZ_GROUP = '92624304'

with open('admin.json', 'r', encoding="utf-8") as f:
    ADMIN = json.loads(f.read())

@qqbot.listener((RcvdGroupMessage, GroupMemberIncrease))
def restriction(message):
    if isinstance(message, (GroupMemberIncrease, )):
        return message.group !=MZ_GROUP
    if message.group != MZ_GROUP:
        return True
    # else
    return False

################  Message Recorder

@qqbot.listener((RcvdGroupMessage,))
def groupchatRecoder(message):
    NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('logs/groupchat.log','a',encoding='gbk') as file:
        file.write(NOW+'    '+str(message)+'\n')

@qqbot.listener((RcvdPrivateMessage, ))
def privateRecoder(message):
    NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('logs/privatechat.log','a',encoding='gbk') as file:
        file.write(NOW+'    '+str(message)+'\n')

################   Welcome infomation
@qqbot.listener((GroupMemberIncrease, ))
def join(message):
    qqbot.send(SendGroupMessage(
        group=message.group,
        text="{} 欢迎来到民政统计群，请将群名片改为地区+姓氏的格式。".format(
            CQAt(message.operatedQQ))
    ))

################   About
@qqbot.listener((RcvdGroupMessage, ))
def about(message):
    text = message.text.lower()
    if re.match('^\/about$',text):
        reply(qqbot, message,"Programmed by Chi,This project started at May 2017.\nSpecial thanks to yukixz and CoolQ project.\nAll right reserved by Chi.")


################  Help
@qqbot.listener((RcvdGroupMessage, ))
def help(message):
    text = message.text.lower()
    if re.match('^\/help$',text):
        reply(qqbot, message,"当前主要功能有：\n1、按组织机构代码查询标准库中的信息(database)\n2、按区划代码查询区划信息(database)\n3、校验统一社会信用代码(a simple calculator)\n4、FAQ\n/help\n/about")

'''@TODO
################   search web
@qqbot.listener((RcvdPrivateMessage, ))
def webSearch(message):
    text = message.text
    if re.match('^\/search\s',text):
        reply(qqbot, message, "[CQ:at,qq={}] 搜索结果：https://www.baidu.com/s?wd={}".format(message.qq,text[8:len(text)]))
    else:
        print("false")
'''

################
# repeat
################
REPEAT_QUEUE_SIZE = 20
REPEAT_COUNT_MIN = 2
REPEAT_COUNT_MAX = 4
queue = deque()


class QueueMessage:
    def __init__(self, text):
        self.text = text
        self.count = 0
        self.senders = set()
        self.repeated = False


class RandomQueue:
    def __init__(self, init, time=1):
        self.init = init
        self.time = time
        self.queue = []

    def next(self):
        if len(self.queue) == 0:
            self.queue = self.time * self.init
            random.shuffle(self.queue)
        return self.queue.pop()


@qqbot.listener((RcvdPrivateMessage))
def repeat(message):
    text = message.text
    sender = message.qq

        # Find & remove matched message from queue.
    msg = None
    for m in queue:
        if m.text == text:
            msg = m
            queue.remove(m)
            break

    # Increase message count
    if msg is None:
        msg = QueueMessage(text)
    msg.senders.add(sender)
    msg.count = len(msg.senders)

    # Push message back to queue
    queue.appendleft(msg)
    if len(queue) > REPEAT_QUEUE_SIZE:
        queue.pop()

        # Repeat message
    if msg.repeated or msg.count < REPEAT_COUNT_MIN:
        return
    if random.randint(1, REPEAT_COUNT_MAX - msg.count + 1) == 1:
        reply(qqbot, message, msg.text)
        msg.repeated = True
        return True


################   FAQ
class FAQObject:
    DEFAULT_INTERVAL = 60

    def __init__(self, opts):
        self.keywords = opts["keywords"]
        self.whitelist = opts.get("whitelist", [])
        self.message = opts["message"]
        self.interval = opts.get("interval", FAQObject.DEFAULT_INTERVAL)
        self.triggered = 0

with open('faq.json', 'r', encoding="utf-8") as f:
    FAQ = []
    faqs = json.loads(f.read())
    for faq in faqs:
        FAQ.append(FAQObject(faq))


@qqbot.listener((RcvdGroupMessage, RcvdPrivateMessage))
def faq(message):
    text = message.text.lower()
    now = time.time()
    for faq in FAQ:
        if not match(text, faq.keywords):
            continue
        if match(text, faq.whitelist):
            return True
        if (now - faq.triggered) < faq.interval:
            return True

        if isinstance(faq.message, list):
            send_text = random.choice(faq.message)
        else:
            send_text = faq.message

        faq.triggered = now
        reply(qqbot, message, "[CQ:at,qq={}]".format(message.qq)+send_text)
        return True

################# Query Organisitions by code
@qqbot.listener((RcvdPrivateMessage, RcvdGroupMessage))
def queryOrgByOrgcode(message):
    texts = message.text
    dartRe = re.search('^([0-9]|[A-Z]){9}$',texts)
    if dartRe == None:
        return
    if validatorBarcode(texts)==False:
        return
    if dartRe != None:
        result = queryOrgByCode(dartRe.group(0))
        if result != '':
            reply(qqbot, message, "[CQ:at,qq={}]\n{}".format(message.qq, result))
        else:
            reply(qqbot, message, "[CQ:at,qq={}] 组织机构代码：{}{}".format(message.qq,dartRe.group(0),'\n机构标准库中查不到此单位'))

################ Query Regioncode By regioncode
@qqbot.listener((RcvdGroupMessage, RcvdPrivateMessage))
def queryRegioninfoByRegioncode(message):
    texts = message.text
    dartRe =re.search('^\d{9}$',texts)
    if dartRe == None:
        return
    if validatorBarcode(texts)==True:
        return
    if dartRe != None:
        result = queryRegionByCode(dartRe.group(0))
        if result != '':
            reply(qqbot, message, "[CQ:at,qq={}]{}".format(message.qq,'查询区划代码：'+dartRe.group(0)+'\n反馈结果：\n'+result))
        else:
            reply(qqbot, message, "[CQ:at,qq={}]区划代码：{}{}".format(message.qq, dartRe.group(0),'\n该代码未被使用过（区县以上）'))

################ USCC validate
@qqbot.listener((RcvdGroupMessage, RcvdPrivateMessage))
def validateUSCC(message):
    text = message.text
    dartRe=re.search('^([0-9]|[A-Z]){18}$',text)
    if  dartRe != None:
        if validator(text)==True:
            reply(qqbot, message, "[CQ:at,qq={}]{}".format(message.qq,'\n统一社会信用代码：'+text+'\n√ 校验正确！√ '))
        else:
            reply(qqbot, message, "[CQ:at,qq={}]{}".format(message.qq,'\n统一社会信用代码：'+text+'\n ×不符合编码规则！×'))

################  @ function test
@qqbot.listener((RcvdGroupMessage,))
def atfunc(message):
    text = message.text
    if re.search('\[CQ:at,qq=87275372\]',text):
        reply(qqbot, message,'[CQ:at,qq={}] '.format(message.qq)+'你要干啥？')
    else:
        return


################  main function
if __name__ == '__main__':
    try:
        qqbot.start()
        scheduler.start()
        print("Running...")
        input()
        print("Stopping...")
    except KeyboardInterrupt:
        pass
