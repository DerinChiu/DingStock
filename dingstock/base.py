import base64
import hashlib
import hmac
import time
import urllib

import requests

from .config import DING_CONFIG, STOCK_CONFIG


class Stock:

    # 股票详情url
    DETAIL_URL = 'https://xueqiu.com/S/'

    def __init__(self, config):

        self.symbol = config['symbol']
        self.holder = config['holder']
        self.detail_url = f'{Stock.DETAIL_URL}{self.symbol}'

         # 持仓量
        self.volume = 0
        # 仓成本
        self.cost = 0
        for hold in config['holds']:
            self.volume += hold['volume']
            self.cost += round(hold['quote'] * hold['volume'], 2)
        # 仓成本单价
        self.quote = round(self.cost / self.volume, 3)
        # 现价
        self.current = 0
        # 当前交易日变动价格
        self.change = 0
        # 当前交易日变动幅度
        self.percent = 0
        # 上次查询变动幅度
        self._last_percent = 0
        self.update()

        # 通知@提醒队列
        self._sn = self.__process_sn(config['strong_notifications'])
        # 通知变动幅度%
        self._notify_amp = config['notify_amp']

    def profit(self):
        return round(self.value() - self.cost, 2)

    def value(self):
        return round(self.current * self.volume, 2)

    def update(self):
        cur = self.__enquiring()
        self.current = cur['current']
        self.percent = cur['percent']
        self.change = cur['chg']

    def is_notify(self):
        if abs(self.percent - self._last_percent) >= self._notify_amp:
            self._last_percent = self.percent
            return True
        return False

    def is_strong_notify(self):
        now = int(time.time())
        for _ in self._sn:
            if abs(self.percent) >= _['threshold']:
                if not _['last_notify']:
                    _['last_notify'] = now
                    return True
                if not _['repeat']:
                    continue
                if now - _['last_notify'] >= _['repeat_min_interval']:
                    _['last_notify'] = now
                    return True
        return False

    def output_markdown(self, at=False):
        md = ""
        if self.change > 0:
            md += f'#### [{self.symbol}]({self.detail_url})  **{self.current}**  <font color=#dd0000>↑{self.change} {self.percent}%</font>  \n'
        elif self.change < 0:
            md += f'#### [{self.symbol}]({self.detail_url})  **{self.current}**  <font color=#006600>↓{self.change} {self.percent}%</font>  \n'
        else:
            md += f'#### [{self.symbol}]({self.detail_url})  **{self.current}**  {self.change} {self.percent}%  \n'

        md += f'> ###### 仓位: **{self.volume}**  持仓价: **{self.quote}**  \n'

        profit = self.profit()
        if profit > 0:
            md += f'> ###### 成本: **{self.cost}**  现值: **{self.value()}**  <font color=#dd0000>↑{profit}</font>'
        elif profit < 0:
            md += f'> ###### 成本: **{self.cost}**  现值: **{self.value()}**  <font color=#006600>↓{profit}</font>'
        else:
            md += f'> ###### 成本: **{self.cost}**  现值: **{self.value()}**  {profit}'
        
        if at:
            md += f'  \n\n@{self.holder}'
        return {'text': md}

    def output(self, at=False):
        out = {
            'data': {
                'text': self.output_markdown(at=at)['text'],
                'btnOrientation': '0',
                'singleTitle': '查看详情',
                'singleURL': self.detail_url
            }
        }
        if at:
            out['at'] = {"atMobiles": [str(self.holder)], "isAtAll": False}
        return out

    def __enquiring(self):
        res = requests.get(
            'https://stock.xueqiu.com/v5/stock/realtime/quotec.json?symbol=' + self.symbol, 
            headers={'User-Agent': ''}
        )
        try:
            return res.json()['data'][0]
        except:
            return {}

    @staticmethod
    def __process_sn(conf):
        for _ in conf:
            _['last_notify'] = 0
        # 按照threshold倒序排列
        return sorted(conf, key=lambda t: t['threshold'], reverse=True)


class Ding:

    def __init__(self, config):
        self.webhook = config['webhook']
        self.key = config['key']

    def send(self, title, content, method='actionCard'):
        content['data'].update({'title': title})
        msg = {'msgtype': method, method: content['data']}
        if 'at' in content:
            msg['at'] = content['at']
        timestamp, sign = self.__get_sign()
        requests.post(f'{self.webhook}&timestamp={timestamp}&sign={sign}', json=msg)

    def __get_sign(self):
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.key.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.key)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign


class ManagerBase:

    def __init__(self):
        self._entities = []
        self.load()

    def load(self):
        raise NotImplementedError

    def entities(self):
        for entity in self._entities:
            yield entity


class DingManager(ManagerBase):

    def load(self):
        for key in DING_CONFIG:
            self._entities.append(Ding(key))


class StockManager(ManagerBase):

    def load(self):
        for key in STOCK_CONFIG:
            self._entities.append(Stock(key))
        