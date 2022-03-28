import requests
import json
import csv
import queue
import threading
import time
import http.client
import urllib
import urllib.request
import urllib.parse
import datetime
import tempfile
import math
import random
import ast
import hmac
import functools
import operator
import statistics
from datetime import date
import pandas as pd
import numpy as np
import pprint 

import bybit

from urllib.request import Request, urlopen
 


class HistoricalPrice(object):

    def __init__(self, host, symbol, interval, timestamp, limit, client):

        self.host = host
        self.symbol = symbol
        self.interval = interval
        self.timestamp = timestamp - (24 * 3600)
        self.limit = limit 
        self.client = client

        self.url = '{}/v2/public/kline/list'.format(self.host)


    def api_historical_response(self):
        r = self.client.LinearKline.LinearKline_get(symbol=self.symbol, interval=self.interval, limit=None, **{'from':int(self.timestamp)}).result() #IS A TYPE TUPLE FOR SOME REASON
        
        for entries in r:
            self.results = entries['result']                
            return self.results

    def volume(self):

        volumes = []

        for result in self.results:
            volumes.append(result['volume'])

            
        return volumes
        

    def price_close(self):

        closes = []


        for result in self.results:
            closes.append(result['close'])

        return closes

    def price_open(self):
        opens = [] 

        for result in self.results:
            opens.append(result['open'])

        return opens


class LivePrice(object):

    def __init__(self, host, param_str, symbol, interval, timestamp):
        self.host = host
         
        self.symbol = symbol
        
        self.url = "{}/v2/public/tickers".format(self.host)




    def price_response(self):
        r = requests.get(self.url)                  #TODO: Insert URL for response
        response = r.text
        response_dict = ast.literal_eval(response)

        return (response_dict)

    def price_dict(self):
        self.response_dict = self.price_response()
        dict_result = list(self.response_dict["result"])

   #     return dict_result

        for result in dict_result:
            if result['symbol'] == self.symbol:
                price = result['last_price']


        return float(price)



class timeStamp(object):

    def __init__(self, client):
        self.client = client
        
    def api_time_request(self):
        r = self.client.Common.Common_get().result()[0]
        time = float(r['time_now'])

 #       print('API TIME: ' + str(r))
        return int(time)

    



def get_signature(api_secret,params):
    '''Encryption Signature'''

    _val = '&'.join([str(k)+"="+str(v) for k, v in sorted(params.items()) if (k != 'sign') and (v is not None)])
    # print(_val)
    return str(hmac.new(bytes(api_secret, "utf-8"), bytes(_val, "utf-8"), digestmod="sha256").hexdigest())

class ExecuteOrder(object):

    def __init__(self,client,symbol,side,size,price,take_profit,stop_loss):

        self.client = client
        self.symbol = symbol
        self.side = side
 #       print(int(price))
  #      print(float(size))
        self.size = size #int(round(int(price) * float(size),0))
        self.price = int(round(price,0))
   #     print(self.size)

        self.take_profit = int(round(take_profit,0))

   #     print(int(self.take_profit))
    #    print(int(self.size))
     #   print(int(self.price))
        self.stop_loss = stop_loss

        if self.side == 'Buy':
            self.base_price = self.price + 50
            self.stop_px = self.price - 50
        elif self.side == 'Sell':
            self.base_price = self.price - 50
            self.stop_px = self.price + 50
  
        
 
        

    def order(self):

    #    client_order = client.Order.Order_newV2(side=self.side,symbol=self.symbol,order_type="Limit",qty=int(self.size),price=int(self.price),time_in_force="ImmediateOrCancel",
    #                                            take_profit=int(self.take_profit),stop_loss=self.stop_loss,order_link_id=None).result()

        client_order = client.LinearOrder.LinearOrder_new(side=self.side,symbol=self.symbol,order_type="Limit",qty=self.size,price=self.price,time_in_force="PostOnly",reduce_only=False,take_profit=int(self.take_profit),stop_loss=self.stop_loss,close_on_trigger=False).result()
  #      client_order = client.LinearConditional.LinearConditional_new(stop_px=self.stop_px, side=self.side,symbol=self.symbol,order_type="Limit",qty=self.size,base_price=self.base_price, price=self.price,time_in_force="PostOnly",reduce_only=False,take_profit=int(self.take_profit),stop_loss=self.stop_loss,close_on_trigger=False).result())
  #      print(client_order)
        for entries in client_order:
            results = entries['result']
            order_id = results['order_id']
            return order_id

      #  print(type(client_order))
     #   result = client_order['result']
     #   print("ORDER RESULT: " + str(result))
     #   order_id = result['order_id']
        
        
      #  return client_order

   
 

        


class Position(object):

    def __init__(self,host,param_str,symbol):

        self.client = client
        self.host = host
        self.params = param_str
        self.symbol = symbol

        self.url = '{}/v2/private/position/list?{}'.format(self.host,self.params)
        

    def wrapper_position(self):
        if "USDT" not in self.symbol:
            r = self.client.Positions.Positions_myPosition().result()
        else:
            r = client.LinearPositions.LinearPositions_myPosition(symbol=self.symbol).result()
        #    return (r)

        try:
            for entries in r:
                results = entries['result']                
                for result in results:
                    if result['side'] == 'Buy':
                        if result['position_value'] == 0:
                            continue
                        else:
                            return result['size']
                    if result['side'] == 'Sell':
                        if result['size'] == 0:
                            return result['size']
                        else:
                            return result['size']
        except Exception:
            return 0

        
                    
        
        
        


    def HTTP_connect_position(self):
        '''NOT IN USE'''        
        print("position host: " + str(self.host))
        print("position params: " + str(self.params))
        r = requests.get(self.url)
        response = r.text
        try:
           response_dict = ast.literal_eval(response)
           dict_result = response_dict['result']
           for result in dict_result.values():
               if result == self.symbol:
                  position_value = dict_result['position_value']
 
           if int(position_value) > 0:
                return True
           else:
                return False
 
        except Exception:
            server_time = int(response[143:156])
            recv_window = int(response[170:174])

            x = server_time - recv_window
            y = server_time + 1000

            print("Timestamp must be greater than this: " + str(server_time - recv_window))
            print("Timestamp must be less than this: " + str(server_time + 1000))

            midpoint = int((y+x)/2)

            print("MIDPOINT: " + str(midpoint))
            

       #     if server_time - recv_window <= timestamp < server_time + 1000:
        #            return timestamp

            
            
            return response

class Wallet(object):

    def __init__(self,client,host,param_str,symbol):

        self.client = client
        self.host = host
        self.params = param_str
        self.symbol = symbol

        self.url = '{}/v2/private/wallet/balance?{}'.format(self.host,self.params)

 

    def HTTP_connect_wallet(self):
        '''NOT IN USE'''
        r = requests.get(self.url)                   
        response = r.text
        try:
           response_dict = ast.literal_eval(response)
           dict_result = response_dict['result']
           for result in dict_result.keys():
                if result == self.symbol[0:3]:
                    balance = dict_result[result]['available_balance']
                
                
     #      print(response) 
           return balance
        except Exception:
            return response

    def wrapper_wallet(self):
        if "USDT" not in self.symbol:
            r = self.client.Wallet.Wallet_getRecords().result()
        else:
            r = client.Wallet.Wallet_getBalance(coin="USDT").result()
      #      return r
        try:
            if "USDT" not in self.symbol:
                for entries in r:
                    results = entries['result']
                    data = results['data']
                    for d in data:
                        if d['coin'] == self.symbol[0:3]:
                            balance = d['wallet_balance']
                            return balance
            else:
                for entries in r:
                    results = entries['result']
                    balance = results["USDT"]
                    for balances in balance:
                        available_balance = balance['available_balance']
                        return available_balance
        except Exception:
            return r
        
    #    return "done" 
        
         
 

def LB(SMA,closes):
    '''Lower Bollinger Band'''
    return SMA - (statistics.stdev(closes)*2)

def UB(SMA,closes):
    '''Upper Bollinger Band'''
    return SMA + (statistics.stdev(closes) * 2)


def SMA(closes):
    '''20 Day Simple Moving Average Calculation'''

    return sum(closes) / len(closes)

def EMA(closes):
    '''Exponential moving averages over a period of time'''

    multiplier = 2/(len(closes) + 1)  
    previous_day = SMA(closes)
    return (closes[-1] - previous_day) * multiplier + previous_day

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
    

 
    


def trade(host, param_str, symbol, interval, timestamp, params, limit, client, api_time, api_key, signature):
    """The Actual Strategy """

    break_even = []

    upper_trigger = []
    lower_trigger = []

    triggered = False 

    first_reduction = False
    second_reduction = False
    third_reduction = False
    
    historical_price = HistoricalPrice(host, symbol, interval, api_time, limit, client)
    api_historical_response = historical_price.api_historical_response()
    closes = historical_price.price_close()
 #   print("CLOSES: " + str(closes))
    volume = historical_price.volume()
    volume_sma = SMA(volume[-20:-1])
#    print(type(volume[-1]))


    simple_moving_average = SMA(closes[-20:-1])
    upper_band = UB(simple_moving_average,closes[-21:-1])
    lower_band = LB(simple_moving_average,closes[-21:-1])

 #   print("Upper Band: " + str(upper_band))
 #   print("Lower Band: " + str(lower_band))

 #   print("Latest Close: " + str(closes[-1]))



    EMA8 = EMA(closes[-9:-1])
    EMA12 = EMA(closes[-13:-1])
    EMA26 = EMA(closes[-27:-1])


   

    list_15 = []

 
    
 

  #  print("EMA 8: " + str(EMA8))
  #  print("EMA 12: " + str(EMA12))
  #  print("EMA 26: " + str(EMA26))
  #  print("SMA: " + str(SMA1))

    positions = Position(host,param_str,symbol)
    position = positions.wrapper_position()
#    print("POSITION: " + str(position))
    
 

    wallet = Wallet(client,host,param_str,symbol)
    size = wallet.wrapper_wallet()
 #   print("Balance: " + str(size))

    live_price = LivePrice(host, param_str, symbol, interval, timestamp)
    price = live_price.price_dict()
  #  print(price)
 
 


    
    
    
    

    while True:
        try:          
            historical_price = HistoricalPrice(host, symbol, interval, api_time, limit, client)
            
            while True:
                try:
                    positions = Position(host,param_str,symbol)
                    position = positions.wrapper_position()
                    if position != None:
                        break
                except Exception:
                    time.sleep(5)
                
            api_historical_response = historical_price.api_historical_response()
            closes = historical_price.price_close()
            latest_closes = closes[-21:-1]
        #    print("closes: " + str(closes))
        #    print("latest closes: " + str(latest_closes))
         #   print(("\n"))

            
       #     time.sleep(60)

            
            if len(closes) == 200:
                time_stamp = timeStamp(client)
                api_time = time_stamp.api_time_request() - ((1*6000))
                historical_price = HistoricalPrice(host, symbol, interval, api_time, limit, client)

                
            EMA8 = EMA(latest_closes[-9:-1])
            EMA12 = EMA(latest_closes[-13:-1])
            EMA26 = EMA(latest_closes[-27:-1])
            simple_moving_average = SMA(latest_closes)
            upper_band = UB(simple_moving_average,latest_closes)
            lower_band = LB(simple_moving_average,latest_closes)
            
            M15 = (list(chunks(closes, 3)))

            for m in M15:
                if len(m) == 2:
                    list_15.append(m[-1])

            list_15 = list_15[-21:-1]

            SMA_15 = SMA(list_15)
            UB_15 = UB(SMA_15, list_15)
            LB_15 = LB(SMA_15, list_15)
            live_price = LivePrice(host, param_str, symbol, interval, timestamp)
            price = live_price.price_dict()
            

                
            if position == 0:
                                       
                if upper_band < latest_closes[-1] and (live_price > UB_15 or latest_closes[-1] > UB_15) :
                    break_even[:] = []
                    first_reduction = False
                    second_reduction = False
                    third_reduction = False
                    print("Short order executed.")
                    side = "Sell"
               #     side_order.append(side)
                    wallet = Wallet(client,host,param_str,symbol)
                    size = wallet.wrapper_wallet()
                    balance = wallet.wrapper_wallet()
                    live_price = LivePrice(host, param_str, symbol, interval, timestamp)
                    price = live_price.price_dict() + 0.5
                
                    print("Order Size: " + str(size))

                    size = round((float(size) / int(price)),4) 
                    print("SIZE: " + str(size))

         #           size = round((float(size)/int(price)),4)
                    take_profit = EMA26
                    stop_loss = int(int(price) + (int(price) * 0.01))
                    print("Price: " + str(price))
                    print("Stop Loss: " + str(stop_loss))
                    print("Take Profit: " + str(take_profit))
                    order = ExecuteOrder(client,symbol,side,size,price,take_profit,stop_loss)
              #      if len(side_order) >= 2:
             #           if side_order[-2] != side_order[-1]:
                    execute = order.order()
                    print(execute)
                    time.sleep(300)
              #      print(client.LinearConditional.LinearConditional_cancelAll(symbol=symbol).result())
                    positions = Position(host,param_str,symbol)
                    position = positions.wrapper_position()
                    if position > 0:
                        continue
                    else:
                        print(client.LinearOrder.LinearOrder_cancel(symbol=symbol, order_id=execute).result())
                        print(client.LinearOrder.LinearOrder_cancelAll(symbol=symbol).result())
                        print(client.LinearConditional.LinearConditional_cancel(symbol=symbol, stop_order_id=execute).result())
                        print(client.LinearConditional.LinearConditional_cancelAll(symbol=symbol).result())

                    break_even.append(price)
                    size = round(size,3)
             #       else:
             #           upper_trigger[:] = []
                        

                
                if lower_band > latest_closes[-1] and (live_price < LB_15 or latest_closes[-1] < LB_15):# and (volume_sma * 2) > volume[-1]:# and len(lower_trigger) >= 1 and latest_closes[-2] == lower_trigger[-1]:           #long position
               #     print("latest closes: " + str(latest_closes[-1]))              
               #     print("EMA 8 : " + str(EMA8) + " EMA 26: " + str(EMA26))
               #     print("Long position")
               #     live_price = LivePrice(host, param_str, symbol, interval, timestamp)
               #     price = live_price.price_dict()
               #     print("Lower trigger length: " + str(lower_trigger_len))
                #    if int(latest_closes[-1]) < int(EMA8) and int(EMA26) > int(latest_closes[-1]) and latest_closes[-lower_trigger_len] == lower_trigger[-lower_trigger_len]:
                    break_even[:] = []
                    first_reduction = False
                    second_reduction = False
                    third_reduction = False
                    print("Long order executed.")
                    side = "Buy"
                #    side_order.append(side)
                    wallet = Wallet(client,host,param_str,symbol)
                    size = wallet.wrapper_wallet()
     
                    
                    balance = wallet.wrapper_wallet()
                    live_price = LivePrice(host, param_str, symbol, interval, timestamp)
                    price = live_price.price_dict() - 0.5

                    
                    size = round((float(size)/int(price)),4) 

                    print("Order Size: " + str(size))
                    
             
            #        size = round((float(size)/int(price)),4)
                    take_profit = EMA26
                    stop_loss = int(int(price) - (int(price) * 0.01))

                    print("Price: " + str(price))
                    print("Take Profit: " + str(take_profit))
                    print("Stop Loss: " + str(stop_loss))
                    order = ExecuteOrder(client,symbol,side,size,price,take_profit,stop_loss)
              #      if len(side_order) >= 2:
                #        if side_order[-2] != side_order[-1]:
                    execute = order.order()
                    print(execute)
                    time.sleep(300)
                    positions = Position(host,param_str,symbol)
                    position = positions.wrapper_position()
                    if position > 0:
                        continue
                    else:
                        print(client.LinearOrder.LinearOrder_cancel(symbol=symbol, order_id=execute).result())
                        print(client.LinearOrder.LinearOrder_cancelAll(symbol=symbol).result())
                        print(client.LinearConditional.LinearConditional_cancel(symbol=symbol, stop_order_id=execute).result())
                        print(client.LinearConditional.LinearConditional_cancelAll(symbol=symbol).result())

                    break_even.append(price)
             #       else:
             #           lower_trigger[:] = []
                        
         
            elif position > 0:
            #    print(break_even[-1])
                balance = wallet.wrapper_wallet()
                if side == "Buy":
                    live_price = LivePrice(host, param_str, symbol, interval, timestamp)
                    price = live_price.price_dict()
                    if price <= LB_15:
                        r = client.LinearOrder.LinearOrder_new(side="Sell",symbol=symbol,order_type="Market",qty=(position),price=price,time_in_force="FillOrKill",reduce_only=True, close_on_trigger=True).result()     

                        
                    
                    if price >= EMA8:
                        while first_reduction == False:
                            balance = positions.wrapper_position()
                            r = client.LinearOrder.LinearOrder_new(side="Sell",symbol=symbol,order_type="Limit",qty=(position*0.33),price=price,time_in_force="FillOrKill",reduce_only=True, close_on_trigger=True).result()
           #                print("Order: " + str(r))
                            new_balance = positions.wrapper_position()
                            print("Balance: " + str(balance) + " New balance: " + str(new_balance))
                            if new_balance != balance:
                               print("EMA 8: " + str(EMA8))
                               print("First Reduction.")
                               first_reduction = True
                            
                    if price >= EMA12:
                        while second_reduction == False:
                            balance = positions.wrapper_position()   
                            r = client.LinearOrder.LinearOrder_new(side="Sell",symbol=symbol,order_type="Limit",qty=(position*0.33),price=price,time_in_force="FillOrKill",reduce_only=True, close_on_trigger=True).result()    
              #              print(client.Positions.Positions_tradingStop(symbol=symbol,stop_loss=break_even[-1]).result())
                            new_balance = positions.wrapper_position()
                            print("Balance: " + str(balance) + " New balance: " + str(new_balance))
                            if new_balance != balance:
                                second_reduction = True
                                print("Second Reduction.")
                                print("EMA 12: " + str(EMA12))
                                
                    if price >= EMA26:
                        while third_reduction == False:
                            balance = positions.wrapper_position()
                            r = client.LinearOrder.LinearOrder_new(side="Sell",symbol=symbol,order_type="Limit",qty=(position),price=price,time_in_force="FillOrKill",reduce_only=True, close_on_trigger=True).result()     
                            new_balance = positions.wrapper_position()
                            print("Balance: " + str(balance) + " New balance: " + str(new_balance))
                            if new_balance != balance:
                                third_reduction = True
                                print("Third Reduction Position Close.")
                                print("EMA 26: " + str(EMA26))

                    if price <= int(break_even[-1]) and second_reduction == True:
                        print("break even hit")
                        balance = positions.wrapper_position()
                        r = client.LinearOrder.LinearOrder_new(side="Sell",symbol=symbol,order_type="Limit",qty=(position),price=price,time_in_force="FillOrKill",reduce_only=True, close_on_trigger=True).result()     
                        new_balance = positions.wrapper_position()
                        if new_balance != balance:
                            break
                        
                        print("New Break Even" + str(r))

                        
                        

                elif side == "Sell":
                    live_price = LivePrice(host, param_str, symbol, interval, timestamp)
                    price = live_price.price_dict()
                    if price >= UB_15:
                        r = client.LinearOrder.LinearOrder_new(side="Buy",symbol=symbol,order_type="Market",qty=(position),price=price,time_in_force="FillOrKill",reduce_only=True, close_on_trigger=True).result()     
 
                        
                    if price <= EMA8:
                        while first_reduction == False:
                            balance = positions.wrapper_position()
                            r = client.LinearOrder.LinearOrder_new(side="Buy",symbol=symbol,order_type="Limit",qty=(position*0.33),price=price,time_in_force="FillOrKill",reduce_only=True, close_on_trigger=True).result()
                   #        print("ORDER: " + str(r))
                            new_balance = positions.wrapper_position()
                            if new_balance != balance:                
                               first_reduction = True
                               print("Balance: " + str(balance) + " New balance: " + str(new_balance))
                               print("First Reduction.")
                               print("EMA 8: " + str(EMA8))
                        
                    if price <= EMA12:
                        while second_reduction == False:
                            balance = positions.wrapper_position()                     
                            r = client.LinearOrder.LinearOrder_new(side="Buy",symbol=symbol,order_type="Limit",qty=(position*0.33),price=price,time_in_force="FillOrKill",reduce_only=True, close_on_trigger=True).result()    
                   #        print(client.Positions.Positions_tradingStop(symbol=symbol,stop_loss=break_even[-1]).result())
                            new_balance = positions.wrapper_position()
                            if new_balance != balance:
                                second_reduction = True
                                print("Balance: " + str(balance) + " New balance: " + str(new_balance))
                                print("Second Reduction.")
                                print("EMA 12: " + str(EMA12))
                    
                        
                    if price <= EMA26:
                        while third_reduction == False:
                            
                            balance = positions.wrapper_position()
                            r = client.LinearOrder.LinearOrder_new(side="Buy",symbol=symbol,order_type="Limit",qty=(position),price=price,time_in_force="FillOrKill",reduce_only=True, close_on_trigger=True).result()     
                            new_balance = positions.wrapper_position()
                            if new_balance != balance:
                                third_reduction = True
                                print("Balance: " + str(balance) + " New balance: " + str(new_balance))
                                print("Third Reduction Position Close.")
                                print("EMA 26: " + str(EMA26))


                    if price >= int(break_even[-1]) and second_reduction == True:
                        print("Break even hit")
                        balance = positions.wrapper_position()
                        r = client.LinearOrder.LinearOrder_new(side="Buy",symbol=symbol,order_type="Limit",qty=(position),price=price,time_in_force="FillOrKill",reduce_only=True, close_on_trigger=True).result()     
                        new_balance = positions.wrapper_position()
                        if new_balance != balance:
                            break
                        
                        
                        print("New Break Even" + str(r))
        except Exception:
            continue 
                        
                        

                #If balance drops 1% close position
                #EMA8 = First take profit --> close 1/3
                #EMA12 = Second take profit --> close 1/3   stop loss = break even price
                #EMA26 = Close full position
                        




if __name__ == "__main__":
    # Initializes: API key, leverage, symbol, timestamp

#    print(bitcoin_converter())


    
    timestamp =  int(time.time()*1000) + 4000000 - 310000 #+5000
    timestamp = int(time.time()*1000) + 2500


    api_domain = {"live": "gYLejbEmG7CX49s8iI", "test": "kqqAWmGlLz97i6PeUi"} #Ontario IP: "JOY4FE04n78T30XJ0r"}
    secret = {"live": "xb6lFLoF2fxQSzu1h24YFmZoZJ87", "test": "1cLjP6HsXh0ZJXIFwv0oVxkiuYcqy0tfLMMZ"} #"h7UObGL1FcTYtezWuNH9qolfY32uSAVaShlC"}
    url_domain = {"live": "https://api.bybit.com", "test": "https://api-testnet.bybit.com"}

    domain = "test"

    api_key = api_domain[domain]
    host = url_domain[domain]
    api_secret = secret[domain]

    client = bybit.bybit(test=True, api_key=api_key, api_secret=api_secret)   

  #  print(client.LinearPositions.LinearPositions_switchIsolated(symbol="BTCUSDT",is_isolated=False, buy_leverage=1, sell_leverage=1).result())      #leverage controls
  #  print(client.Positions.Positions_saveLeverage(symbol="BTCUSD", leverage="10").result())                 #leverage controls
    limit = '5'
    
                
                
    

    symbols = ["BTCUSD","ETHUSD","EOSUSD","XPRUSD","BTCUSDT"]

    symbol = "BCHUSDT"
    leverage = "1"
    interval = "5"          #timeframe

    time_stamp = timeStamp(client)
    api_time = time_stamp.api_time_request() - ((1*6000))
    print("API TIME: " + str(api_time)) 
    print("TIMESTAMP: " + str(timestamp))
    
    params = {}
    params['api_key'] = api_domain[domain]
    params['leverage'] = leverage
    params['symbol'] = symbol
    params['timestamp'] = timestamp

    signature = get_signature(api_secret,params)
    param_str = "api_key={}&leverage={}&symbol={}&timestamp={}&sign={}".format(api_key, leverage, symbol, timestamp, signature)  # Parameter required for HTTP requests
  #  positions = Position(host,param_str,symbol)
   # position = positions.HTTP_connect_position()    
    #timestamp = position

       

    trade(host, param_str, symbol, interval, timestamp, params, limit, client, api_time, api_key, signature)

 

# IMPORTANT:
# 10002 Error code caused by misaligned server time and OS clock. Sync OS clock to fix problem
