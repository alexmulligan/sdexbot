from random import randint
from os import listdir, path, mkdir
import csv
import sqlite3

# TODO: Currently, the program will append to logs which already exist (from log_id), but the counter resets every time.
#       I need to implement functionality that will resume the counter from what is already in the log files
# TODO: Possibly implement rounding to the nearing integer (second) for timestamp?
class Logger:
    """Data Format:

   id: ex. 2 - simple counter that increases when each trade is logged
   timestamp: ex. 1619140934 - datetime in seconds when order was placed (normal python datetime.timestamp() but rounded to integer)
   action: ex. BUY - type of trade made. refers to base (non-XLM) asset; bought USDC (sold XLM)
   symbol: ex. USDC-GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN - base asset; code-issuer
   volume: ex. 20.685232 - amount traded in quote asset (XLM)
   currency: ex. XLM - quote asset; usually just XLM
   price: ex. 2.3881395 - price of base in quote asset; usually just price in XLM

   """

    _counter = 0

    def __init__(self, type='all', log_id=None, file_prefix='sdexbot_log-'):
        if type == 'all':
            self.csv = True
            self.db = True
        elif type == 'csv':
            self.csv = True
        elif type == 'db':
            self.csv = True
        else:
            raise Exception('Logger: Invalid type specified')

        if log_id == None:
            self.log_id = randint(1000, 9999) # TODO: fix this so it has no chance of generating an already used id number
        else:
            self.log_id = log_id

        if not path.exists('log'):
            mkdir('log')

        if self.csv:
            self.csv_path = path.join('log', file_prefix + str(self.log_id) + '.csv')
            self._initialize_csv()

        if self.db:
            self.db_path = path.join('log', file_prefix + str(self.log_id) + '.db')
            self._initialize_db()


    ############## Public Methods ###############


    def log(self, trade_data):
        self._counter += 1

        if self.csv:
            dataList = [self._counter, trade_data['timestamp'], trade_data['action'], trade_data['symbol'], trade_data['volume'], trade_data['currency'], trade_data['price']]

            with open(self.csv_path, 'a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(dataList)

        if self.db:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.execute("INSERT INTO trades VALUES ({}, {}, '{}', '{}', {}, '{}', {})".format(self._counter, trade_data['timestamp'], trade_data['action'].upper(), trade_data['symbol'], trade_data['volume'], trade_data['currency'], trade_data['price']))
            con.commit()
            con.close()


    # TODO: implement this function; maybe have it just print out the data in a table format?
    def read_log(self):
        pass

    ############## Private Methods ###############


    def _initialize_csv(self):
        if not path.exists(self.csv_path):
            with open(self.csv_path, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(['id', 'timestamp', 'action', 'symbol', 'volume', 'currency', 'price'])


    def _initialize_db(self):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY,
            timestamp INTEGER NOT NULL,
            action TEXT NOT NULL,
            symbol TEXT NOT NULL,
            volume REAL NOT NULL,
            currency TEXT NOT NULL,
            price REAL NOT NULL
        );
        """)
        con.close()
