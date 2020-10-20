
# -*- coding:utf-8 -*-

import os
import re
import json
import logging
import requests
import datetime as dt
from time import sleep
from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler

class SubFormatter(logging.Formatter):
    converter=dt.datetime.fromtimestamp
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s

class Logging(object):
    def __init__(self, log_dir='./logs', log_name='server', console=True):
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.DEBUG)
        formatter = SubFormatter(fmt='%(asctime)s [%(name)s] [%(funcName)s:%(lineno)s] [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S.%f')

        # file handler
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = log_dir + '/' + log_name
        fh = TimedRotatingFileHandler(filename=log_file, when="H", interval=1, backupCount=3*24)
        fh.suffix = "%Y-%m-%d_%H-%M.log"
        fh.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}.log$")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        # console handler
        if console:
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def getLogger(self):
        return self.logger

headers = {"content-type": "application/json"}
cli_wallet_url = "http://127.0.0.1:8048"

token = "xxx"
alert_address = "https://oapi.dingtalk.com/robot/send?access_token="+token

logger = Logging().getLogger()

account_list = ["nicotest", "init1"]
# asset_type = ["COCOS", "GAS"]

# 1.3.0 -- COCOS, 1.3.1 -- GAS
asset_limit = {"1.3.0":1000, "1.3.1": 80000000}

def send_message(messages, label=['faucet']):
    try:
        body_relay = {
            "jsonrpc": "2.0",
            "msgtype": "text",
            "text": {
                "content": str(label) + str(messages)
            },
            "id":1
        }
        response = json.loads(requests.post(alert_address, data = json.dumps(body_relay), headers = headers).text)
        logger.debug('request response: {}'.format(response))
    except Exception as e:
        logger.error("task error: '{}'".format(repr(e)))

def task():
    while True:
        messages = []
        for account in account_list:
            req_data = {
                "jsonrpc": "2.0",
                "method": "list_account_balances",
                "params": [account],
                "id":1
            }
            logger.debug('>> {} {}'.format(req_data['method'], req_data['params']))
            try:
                response = json.loads(requests.post(cli_wallet_url, data = json.dumps(req_data), headers = headers).text)
                if 'error' in response:
                    msg = "{} {} failed. error: {}".format(req_data['method'], req_data['params'], response['error'])
                    logger.error(msg)
                    # send_message(msg)
                    messages.append(msg)
                    continue
                balances = response['result']
                logger.debug('{} balances: {}'.format(account, balances))
                #[{u'asset_id': u'1.3.0', u'amount': u'9779999894267348'}, {u'asset_id': u'1.3.1', u'amount': 14799662}]
                for balance in balances:
                    asset_id = balance['asset_id']
                    if asset_id in asset_limit:
                        #limit = asset_limit['asset_id']
                        if int(balance['amount']) < asset_limit[asset_id]:
                            msg = "{} asset({}) balance({}) < limit({})".format(account, asset_id, balance['amount'], asset_limit[asset_id])
                            logger.warn(msg)
                            messages.append(msg)       
            except Exception as e:
                logger.error("task error: '{}'".format(repr(e)))
        if messages:
            logger.info('messages: {}'.format(messages))
            send_message(messages)
        sleep(5)

def main():
    task()


if __name__ == '__main__':
    main()

