from stellar_sdk import Server, Network, Asset
from trader import Trader
from datetime import datetime, timedelta
from typing import List, Dict
from statistics import mean

RESOLUTION_ENUM = {
    '1MIN': 60000,
    '5MIN': 300000,
    '15MIN': 900000,
    '1HOUR': 3600000,
    '1DAY': 86400000,
    '1WEEK': 604800000
}


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


def get_sma(price_data: List[float]) -> List[float]:
    """Simple Moving Average

    """

    result = price_data[:]


def get_ema(price_data: List[float]) -> List[float]:
    """Expontential Moving Average

    """

    pass


def get_momentum(price_data: List[float]) -> List[float]:
    """

    """

    pass
