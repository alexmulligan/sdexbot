from stellar_sdk import Server, Network, Asset
from trader import Trader
from datetime import datetime, timedelta
from typing import List, Dict
from statistics import mean

# "blank" dictionary defining each data set to fetch, and parameters for when it should be updated
blank_data_store = {
    'three_weeks': {
        'timeout': timedelta(hours=12),
        'last_fetch': datetime(1999, 1, 1),
        'duration': timedelta(days=21),
        'period': 3600000, # 1 hour
        'data': []
    },
    'two_days': {
        'timeout': timedelta(hours=1),
        'last_fetch': datetime(1999, 1, 1),
        'duration': timedelta(days=2),
        'period': 900000, # 15 minutes
        'data': []
    },
    'hour': {
        'timeout': timedelta(seconds=5),
        'last_fetch': datetime(1999, 1, 1),
        'duration': timedelta(hours=1),
        'period': 60000, # 1 minute
        'data': []
    }
}


def get_historical_data(trader: Trader, time_back: timedelta, period: int) -> List[float]:
    """This method returns a list of historical price data of a SDEX trading pair

    Parameters:
    trader: Trader - Trader object currently being used; needed for trading pair and server instance
    time_back: TimeDelta - amount of time in the past at which the price data should start
    period: int - interval of time (in seconds) between each price data point; ex. 3600000 for 1 hour

    """

    end = datetime.now()
    end_timestamp = round(end.timestamp()*1000)

    start = end - time_back
    start_timestamp = round(start.timestamp()*1000)

    data = []
    records = trader.server.trade_aggregations(trader.quote, trader.base, period, start_timestamp, end_timestamp, 0).cursor('now')

    curr = records.call()
    while curr['_embedded']['records'] != []:
        for record in curr['_embedded']['records']:
            data.append(record['close'])

        curr = records.next()

    float_data = []
    for d in data:
        float_data.append(float(d))

    return float_data


def get_current_avgs(trader: Trader, data_store):
    """

    """

    # Update data only at certain intervals, as to not take too much time.
    for k in data_store.keys():
        if (datetime.now() - data_store[k]['last_fetch']) >= data_store[k]['timeout']:
            data_store[k]['data'] = get_historical_data(trader, data_store[k]['duration'], data_store[k]['period'])
            data_store[k]['last_fetch'] = datetime.now()
    
    # Averages based on 1 week data
    three_weeks_data = data_store['three_weeks']['data']
    three_weeks_len = len(three_weeks_data)
    one_week_index = round(three_weeks_len / 3) * 2
    week_avg = round(mean(data_store['three_weeks']['data'][one_week_index:]), 6)

    # Averages based on 2 day data
    two_days_data = data_store['two_days']['data']
    two_days_len = len(two_days_data)
    
    one_day_index = round(two_days_len / 2)
    half_day_index = round(two_days_len / 4) + one_day_index
    six_hour_index = round(two_days_len / 8) + half_day_index
    three_hour_index = round(two_days_len / 16) + six_hour_index

    two_day_avg = round(mean(data_store['two_days']['data']), 6)
    one_day_avg = round(mean(data_store['two_days']['data'][one_day_index:]), 6)
    half_day_avg = round(mean(data_store['two_days']['data'][half_day_index:]), 6)
    six_hour_avg = round(mean(data_store['two_days']['data'][six_hour_index:]), 6)
    three_hour_avg = round(mean(data_store['two_days']['data'][three_hour_index:]), 6)

    # Averages based on 1 hour data
    one_hour_data = data_store['hour']['data']
    one_hour_len = len(one_hour_data)

    half_hour_index = round(one_hour_len / 2)
    fifteen_min_index = round(one_hour_len / 4) + half_hour_index

    one_hour_avg = round(mean(one_hour_data), 6)
    half_hour_avg = round(mean(one_hour_data[half_hour_index:]), 6)
    fifteen_min_avg = round(mean(one_hour_data[fifteen_min_index:]), 6)

    result = {
        'week': week_avg,
        'two_day': two_day_avg,
        'one_day': one_day_avg,
        'half_day': half_day_avg,
        'six_hour': six_hour_avg,
        'three_hour': three_hour_avg,
        'one_hour': one_hour_avg,
        'half_hour': half_hour_avg,
        'fifteen_min': fifteen_min_avg
    }

    return result


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
