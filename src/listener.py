from trader import Trader
from logger import Logger
from data_utils import *
from stellar_sdk import Asset, Server
from dateutil import parser
from datetime import datetime

settings = {
    'secret_key': '',
    'log_id': 0,
    'log_type': 'db',
    'print_trades': True
}
last_cursor = 'now'
serv = Server('https://horizon.stellar.org')
xlm = Asset.native()
usdc = Asset('USDC', 'GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN')


def init():
    global settings
    global trader
    global logger

    if settings['secret_key'] == '':
        my_secret_key = input('Enter Secret Key: ').strip().upper()
        settings['secret_key'] = my_secret_key

    if settings['log_id'] == None:
        log_number_input = int(input('Enter Log ID to resume (leave blank to skip): ').strip())
        settings['log_id'] = log_number_input if log_number_input > 0 else None

    if settings['log_type'] == '':
        log_type_input = input('Enter log type (db, csv, all): ').strip().lower()
        settings['log_type'] = log_type_input

    trader = Trader(serv, settings['secret_key'], usdc, xlm)
    logger = Logger(type=settings['log_type'], log_id=settings['log_id'])
    logger.set_last_id()


def convert_time(ledger_close_time: str) -> datetime:
    utc_time = parser.isoparse(ledger_close_time)
    local_time = utc_time.astimezone()
    return local_time


def handle_trade(response):
    timestamp = convert_time(response['ledger_close_time']).timestamp()
    action = 'SELL' if response['base_account'] == trader.keypair.public_key else 'BUY'
    symbol = 'XLM' if response['base_asset_type'] == 'native' else response['base_asset_code'] + '-' + response['base_asset_issuer']
    volume_in_quote = float(response['counter_amount'])
    currency = 'XLM' if response['counter_asset_type'] == 'native' else response['counter_asset_code'] + '-' + response['counter_asset_issuer']
    price_in_quote = round(float(response['price']['n']) / float(response['price']['d']), 7)
    
    trade_data = {
            'timestamp': round(timestamp),
            'action': action,
            'symbol': symbol,
            'volume': volume_in_quote,
            'currency': currency,
            'price': price_in_quote
        }

    logger.log(trade_data)
    if settings['print_trades']:
        print(f"Trade Logged @ {datetime.fromtimestamp(trade_data['timestamp']).strftime('%-H:%M:%S')}")
        print_dict(trade_data)
        print()


def main():
    init()
    print(f'Listening to {trader.keypair.public_key}\n\n')

    for trade in serv.trades().for_account(trader.keypair.public_key).cursor('now').stream():
        print(f'Handling Trade:')
        handle_trade(trade)
    

if __name__ == '__main__':
    main()
