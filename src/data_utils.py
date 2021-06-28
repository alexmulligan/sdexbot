from stellar_sdk import Server, Network, Asset
from trader import Trader
from datetime import datetime, timedelta
from typing import List, Dict
from statistics import mean
import requests

RESOLUTION_ENUM = {
    '1MIN': 60000,
    '5MIN': 300000,
    '15MIN': 900000,
    '1HOUR': 3600000,
    '1DAY': 86400000,
    '1WEEK': 604800000
}


def print_dict(d, indent=0):
    for k in d.keys():
        if type(d.get(k)) == dict:
            print("{}{}:".format('\t'*indent, k))
            print_dict(d.get(k), indent=indent+1)
        else:
            print("{}{}: {}".format('\t'*indent, k, d.get(k)))


def get_orderbook_url(trader: Trader) -> str:
    """todo"""
    url = 'https://horizon.stellar.org/order_book?'
    params = []
    if trader.quote.is_native():
        params.append('buying_asset_type=native')
    else:
        params.append(f'buying_asset_type={trader.quote.type}')
        params.append(f'buying_asset_code={trader.quote.code}')
        params.append(f'buying_asset_issuer={trader.quote.issuer}')

    if trader.base.is_native():
        params.append('selling_asset_type=native')
    else:
        params.append(f'selling_asset_type={trader.base.type}')
        params.append(f'selling_asset_code={trader.base.code}')
        params.append(f'selling_asset_issuer={trader.base.issuer}')

    limit = 20
    params.append(f'limit={limit}')

    for i in range(0, len(params)):
        if i == 0:
            url += params[i]
        else:
            url += '&' + params[i]
    
    return url


def get_orders(trader: Trader):
    """todo"""
    url = get_orderbook_url(trader)
    res = requests.get(url)
    data = res.json()
    bids = data['bids']
    asks = data['asks']
    return bids, asks


def find_bid(bids, t_depth: float):
    """todo"""
    price = 0.0
    depth = 0.0
    for b in bids:
        price = float(b['price'])
        depth += float(b['amount'])
        if depth >= t_depth:
            break
    
    return round(price - 0.000001, 7)


def find_ask(asks, t_depth: float):
    """todo"""
    price = 0.0
    depth = 0.0
    for a in asks:
        price = float(a['price'])
        depth += float(a['amount'])
        if depth >= t_depth:
            break
    
    return round(price + 0.000001, 7)


def get_historical_data(trader: Trader, time_back: timedelta, resolution: str):
    """This method returns a list of historical price data of a SDEX trading pair

    Parameters:
    trader: Trader - Trader object currently being used; needed for trading pair and server instance
    time_back: TimeDelta - amount of time in the past at which the price data should start
    resolution: str - interval of time between each price data point; see RESOLUTION_ENUM

    """
    end = datetime.now()
    end_timestamp = round(end.timestamp()*1000)
    start = end - time_back
    start_timestamp = round(start.timestamp()*1000)

    price_data = []
    volume_data = []
    records = trader.server.trade_aggregations(trader.base, trader.quote, RESOLUTION_ENUM[resolution], start_timestamp, end_timestamp, 0)#.cursor('now')
    
    curr = records.call()
    while curr['_embedded']['records'] != []:
        for record in curr['_embedded']['records']:
            price_data.append(float(record['close']))
            volume_data.append(float(record['counter_volume']))

        curr = records.next()

    return price_data, volume_data


def get_sma(price_data: List[float], num:int=8) -> List[float]:
    """Simple Moving Average"""
    result = []
    for i in range(0, len(price_data)):
        if i < num:
            if i == 0:
                current_avg = price_data[0]
            else:
                subset = price_data[0:i+1]
                current_avg = round(sum(subset) / len(subset), 7)
        else:
            subset = price_data[i-num:i+1]
            current_avg = round(sum(subset) / len(subset), 7)

        result.append(current_avg)

    return result


def get_wma(price_data: List[float], num:int=8) -> List[float]:
    """Weighted Moving Average"""

    result = []
    weights = [i for i in range(1, num+1)]
    
    for i in range(0, len(price_data)):
        if i <= num:
            if i == 0:
                current_avg = price_data[0]
            else:
                subset = price_data[0:i+1]
                short_weights = [i for i in range(1, len(subset)+1)]
                short_weighted_prices = [subset[j] * short_weights[j] for j in range(0, len(subset))]
                current_avg = round(sum(short_weighted_prices) / sum(short_weights), 7)

        else:
            subset = price_data[i-num:i]
            weighted_prices = [subset[j] * weights[j] for j in range(0, len(subset))]
            current_avg = round(sum(weighted_prices) / sum(weights), 7)

        result.append(current_avg)

    return result
