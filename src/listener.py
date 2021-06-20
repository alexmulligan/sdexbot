from trader import Trader
from logger import Logger
from stellar_sdk import Keypair, Asset, Server, Network
from dateutil import parser
from datetime import datetime
import json

my_secret_key = 'MY SECRET KEY'
last_cursor = 'now'

serv = Server('https://horizon.stellar.org')
xlm = Asset.native()
usdc = Asset('USDC', 'GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN')
trader = Trader(serv, my_secret_key, usdc, xlm)

log_number = 11
logger = Logger(type='db', log_id=log_number)


def convert_time(ledger_close_time: str) -> datetime:
    utc_time = parser.isoparse(ledger_close_time)
    local_time = utc_time.astimezone()
    return local_time


def handle_trade(response):
    print(json.dumps(response, indent=4))

for trade in serv.trades().for_account(trader.keypair.public_key).cursor(last_cursor).stream():
    print('handling')
    handle_trade(trade)
