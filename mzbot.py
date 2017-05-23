#!/usr/bin/env python3
# coding: UTF-8

import json
import random
import re
import datetime
import time
from validator import validator

from apscheduler.schedulers.background import BackgroundScheduler
from cqsdk import CQBot, CQAt, RE_CQ_SPECIAL, RcvdPrivateMessage, \
    RcvdGroupMessage, SendGroupMessage, GroupMemberIncrease,  GroupBan
from utils import match, reply
from db.queryOrgs import queryOrgByCode
from db.queryRegions import queryRegionByCode


qqbot = CQBot(11235)
scheduler = BackgroundScheduler(
    timezone='Asia/Tokyo',
    job_defaults={'misfire_grace_time': 60},
    )


################
# Restriction
################
MZ_GROUP = '590149885'

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

################
#Recorder
################

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

################
# FAQ
################
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


@qqbot.listener((RcvdGroupMessage, ))
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
        reply(qqbot, message, send_text)
        return True

################  Query Organisitions by code
@qqbot.listener((RcvdPrivateMessage, RcvdGroupMessage))
def queryOrgByOrgcode(message):
    texts = message.text
    dartRe = re.search('^([0-9]|[A-Z]){9}$',texts)
    if dartRe != None:
        result = queryOrgByCode(dartRe.group(0))
        if result != '':
            reply(qqbot, message, "[CQ:at,qq={}]{}".format(message.qq, result))
        else:
            reply(qqbot, message, "[CQ:at,qq={}] 组织机构代码：{}{}".format(message.qq,dartRe.group(0),'\n机构库中查不到此单位'))

################ Query Regioncode By regioncode
@qqbot.listener((RcvdGroupMessage, RcvdPrivateMessage))
def queryRegioninfoByRegioncode(message):
    texts = message.text
    dartRe =re.search('^\d{9}$',texts)
    if dartRe != None:
        result = queryRegionByCode(dartRe.group(0))
        if result != '':
            reply(qqbot, message, "[CQ:at,qq={}]{}".format(message.qq,'查询区划代码：'+dartRe.group(0)+'\n反馈结果：\n'+result))
        else:
            reply(qqbot, message, "[CQ:at,qq={}]区划代码：{}{}".format(message.qq, dartRe.group(0),'\n该代码未被使用过（区县以上）'))

################
# Join & Leave
################
@qqbot.listener((GroupMemberIncrease, ))
def join(message):
    qqbot.send(SendGroupMessage(
        group=message.group,
        text="{} 欢迎来到民政统计群，请将群名片改为地区+姓氏的格式。".format(
            CQAt(message.operatedQQ))
    ))



#########   USCC校验
@qqbot.listener((RcvdGroupMessage, RcvdPrivateMessage))
def validateUSCC(message):
    text = message.text
    dartRe=re.search('^([0-9]|[A-Z]){18}$',text)
    if  dartRe != None:
        result = validator(text)
        if result==text:
            reply(qqbot, message, "[CQ:at,qq={}]{}".format(message.qq,'  代码：'+text+'\n校验正确！'))
        else:
            reply(qqbot, message, "[CQ:at,qq={}]{}".format(message.qq,'  代码：'+text+'\n不符合编码规则！'))

#####   @ function test
@qqbot.listener((RcvdGroupMessage,))
def atfunc(message):
    text = message.text
    if re.search('\[CQ:at,qq=87275372\]',text):
        reply(qqbot, message,'[CQ:at,qq={}] '.format(message.qq)+'你要干啥？')
    else:
        return


################
# __main__
################
if __name__ == '__main__':
    try:
        qqbot.start()
        scheduler.start()
        print("Running...")
        input()
        print("Stopping...")
    except KeyboardInterrupt:
        pass
