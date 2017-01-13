# -*- coding: utf-8 -*-
"""
雪球社区接口类
Created on 2017/01/13
@author: Wen Gu
@contact: emptyset110@gmail.com
"""
# 以下是自动生成的 #
# --- 导入系统配置
#import dHydra.core.util as util
#from dHydra.core.Vendor import Vendor
#from dHydra.core.Functions import get_vendor
# --- 导入自定义配置
#from connection import *
import connection
#from .const import *
#from .config import *
# 以上是自动生成的 #
#import pytz
import util
import requests
import asyncio
from pandas import DataFrame
import pandas
from datetime import timedelta
import functools
import threading
#import math
import time


class Xueqiu():

    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        # 先爬取一遍雪球页面，获取cookies
        self.session.get(
            "https://xueqiu.com/hq",	headers=connection.HEADERS_XUEQIU,proxies=connection.proxies
        )
        self.mongodb = None

    def login(self, cfg_path=None):
        import hashlib

        username = 'maxingzhe99@126.com' #cfg["xueqiuUsername"]
        pwd = '6547899x'.encode("utf8") #cfg["xueqiuPassword"].encode("utf8")
        pwd = hashlib.md5(pwd).hexdigest().upper()
        res = self.session.post(url=connection.URL_XUEQIU_LOGIN, data=connection.DATA_XUEQIU_LOGIN(
            username, pwd), headers=connection.HEADERS_XUEQIU,proxies=connection.proxies)
        res_json = res.json()
        print(res_json)
#        if "error_code" in res_json:
#            print(res_json)
#            self.logger.warning("{}".format(res_json))

        return res_json()

    """
    stockTypeList 	: list
        ['sha','shb','sza','szb']分别代表沪A，沪B，深A，深B。如果为空则代表获取所有沪深AB股
        e.g: stockTypeList = ['sha','shb']即获取所有沪A沪B
    columns 		:	string
        默认为："symbol,name,current,chg,percent,last_close,open,high,low,volume,amount,market_capital,pe_ttm,high52w,low52w,hasexist"
    """

    def get_stocks(
        self,
        stockTypeList=['sha', 'shb', 'sza', 'szb'],
        columns=connection.CONST_XUEQIU_QUOTE_ORDER_COLUMN
    ):
        for stockType in stockTypeList:
            print("正在从雪球获取：{}".format(connection.EX_NAME[stockType]))
            page = 1
            while True:
                response = self.session.get(
                    connection.URL_XUEQIU_QUOTE_ORDER(page, columns, stockType),
                    headers=connection.HEADERS_XUEQIU,
                    proxies=connection.proxies
                ).json()
                df = DataFrame.from_records(
                    response["data"], columns=response["column"])
                if 'stocks' not in locals().keys():
                    stocks = df
                else:
                    stocks = stocks.append(df)
                if df.size == 0:
                    break
                page += 1
        return stocks

    def get_symbols(
        self,
        stockTypeList=['sha', 'shb', 'sza', 'szb']
    ):
        """
        返回：set
        """
        symbols = self.get_stocks(
            stockTypeList=stockTypeList,
            columns='symbol'
        )
        return set(symbols.symbol)
        
    """
    获取雪球行情/基本面的接口
    """

    def get_quotation(self, symbol=None, symbolSet=None, dataframe=True, threadNum=3):
        if 'quotation' in self.__dict__.keys():
            del(self.quotation)
            # Cut symbolList
        symbolList = list(symbolSet)
        threads = []
        symbolListSlice = util.slice_list(num=threadNum, data_list=symbolList)
        for symbolList in symbolListSlice:
            loop = asyncio.new_event_loop()
            symbolsList = util.slice_list(step=50, data_list=symbolList)
            tasks = [self.get_quotation_task(
                symbols=symbols) for symbols in symbolsList]
            t = threading.Thread(target=util.thread_loop, args=(loop, tasks))
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        if dataframe:
            self.quotation = DataFrame.from_records(self.quotation).T
        return(self.quotation)

    @asyncio.coroutine
    def get_quotation_task(self, symbols):
        symbols = util.symbols_to_string(symbols)
        quotation = yield from self.fetch_quotation_coroutine(symbols=symbols)
        if 'quotation' not in self.__dict__.keys():
            self.quotation = quotation
        else:
            self.quotation.update(quotation)

    """
    雪球单股基本面数据获取coroutine
    """
    @asyncio.coroutine
    def fetch_quotation_coroutine(self, symbols=None):
        loop = asyncio.get_event_loop()
        if symbols is not None:
            async_req = loop.run_in_executor(
                None,
                functools.partial(
                    self.session.get,
                    connection.URL_XUEQIU_QUOTE(symbols),
                    headers=connection.HEADERS_XUEQIU
                )
            )
            try:
                quotation = yield from async_req
            except Exception as e:
                print(e)
                async_req = loop.run_in_executor(
                    None,
                    functools.partial(
                        self.session.get,
                        connection.URL_XUEQIU_QUOTE(symbols),
                        headers=connection.HEADERS_XUEQIU
                    )
                )
                quotation = yield from async_req
            quotation = quotation.json()
        return(quotation)

    # """
    # 雪球单股基本面数据获取
    # 默认返回值格式是dict，若参数dataframe为True则返回dataframe
    # """
    # def fetch_quotation(self, symbols = None, dataframe = False):
    # 	symbols = util.symbols_to_string(symbols)
    # 	if symbols is not None:
    # 		quotation = self.session.get(
    # 			URL_XUEQIU_QUOTE(symbols)
    # 		,	headers = HEADERS_XUEQIU
    # 		).json()
    # 	if dataframe:
    # 		quotation = DataFrame.from_records( quotation ).T
    # 	return(quotation)

    """
    雪球历史k线接口，包括前/后复权(默认不复权)
        period: 1day,1week,1month
    """

    def get_kline(self, symbol, period='1day', fqType='normal', begin=None, end=None, dataframe=True):
        if end is None:
            end = util.time_now()
        if isinstance(begin, str):
            begin = util.date_to_timestamp(begin)
        if isinstance(end, str):
            end = util.date_to_timestamp(end)
        try:
            response = self.session.get(
                connection.URL_XUEQIU_KLINE(symbol=symbol, period=period, fqType=fqType, begin=begin, end=end),	headers=connection.HEADERS_XUEQIU,proxies=connection.proxies,	timeout=3
            )
            kline = response.json()
            # time.sleep(0.5)
        except Exception as e:
            self.logger.warning("{}".format(e))
            self.logger.info(response.text)
            time.sleep(3)
            return False

        if kline["success"] == 'true':
            if dataframe:
                if (kline["chartlist"] is not None) and (kline["chartlist"] != []):
                    df = DataFrame.from_records(kline["chartlist"])
                    df["time"] = pandas.to_datetime(df["time"])
                    df["time"] += timedelta(hours=8)
                    df["symbol"] = symbol
                    return df
                else:
                    return DataFrame()
            else:
                return kline["chartlist"]
        else:
            return None

    """
    period  = '1d'  	只显示当日分钟线
            = '5d'		5分钟线，250行（最多5个交易日）
            = 'all'		历史周线
    """

    def get_today(self, symbol, period='1day', dataframe=True):
        quotation = self.session.get(
            connection.URL_XUEQIU_CHART(symbol=symbol, period=period),	headers=connection.HEADERS_XUEQIU,proxies=connection.proxies
        ).json()
        if quotation["success"] == "true":
            if dataframe:
                df = DataFrame.from_records(quotation["chartlist"])
                df["time"] = pandas.to_datetime(df["time"])
                df["time"] += timedelta(hours=8)
#                df["hhmm"] = time(df["time"]).strftime('%H:%M')
                
                df["symbol"] = symbol
                return df
            else:
                return quotation #["chartlist"]
        else:
            return False

    def get_combination(self, symbol):
        response = self.session.get(
            "https://xueqiu.com/cubes/nav_daily/all.json?cube_symbol={}&since=0&until=1469611785000"
            .format(symbol),
            headers=connection.HEADERS_XUEQIU,proxies=connection.proxies
        )
        print(response)
        print(response.text)

    """
    雪球键盘助手
    """

    def keyboard_helper(self, symbol):
        response = self.session.get(
            "https://xueqiu.com/stock/search.json?code=%s&size=10&_=%s" % (
                symbol, int(time.time() * 1000))
                ,proxies=connection.proxies
        ).json()["stocks"]
        return response

if __name__ == '__main__':
    xq = Xueqiu()
#    (xq.login())
    q = 'SH600036'
    print(time.ctime())
#    df = xq.get_today(q)
#    df['current'].plot()
#    df.to_excel('output/' + q + '.xlsx')
#    print(time.ctime())
    
#    with open('output/' + q + '.json','w',encoding='utf-8') as f:
#        f.write(str(xq.get_today(q,dataframe=False)))
    
    df = xq.get_stocks(stockTypeList=['shb'])
    df.to_excel('output/list.xlsx')
    print(time.ctime())