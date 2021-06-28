from random import randint
from os import listdir, path, mkdir
import csv
import sqlite3

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

    def __init__(self, type='db', log_id=None, file_prefix='sdexbot_log-'):
        if type == 'all':
            self.csv = True
            self.db = True
        elif type == 'csv':
            self.csv = True
            self.db = False
        elif type == 'db':
            self.db = True
            self.csv = False
        else:
            raise Exception('Logger: Invalid type specified')

        if log_id == None:
            rand_id = randint(0, 100)
            while file_prefix + str(rand_id) + '.db' in listdir() or file_prefix + str(rand_id) + '.csv' in listdir(): # keep generating new random id's if current id is already used
                rand_id = randint(0, 100)
            self.log_id = rand_id
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


    def read_log(self):
        result = ''
        if self.csv:
            with open(self.csv_path, 'r') as f:
                for row in f:
                    current_line = '|'
                    for item in row:
                        current_line += f' {item} |'
                    result += current_line + '\n' + '-'*len(current_line) + '\n'

        elif self.db:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            data = cur.execute("SELECT * FROM trades;").fetchall()
            con.close()
            
            for row in data:
                current_line = '|'
                for item in row:
                    current_line += f' {item} |'
                result += current_line + '\n' + '-'*len(current_line) + '\n'

        else:
            return None
        
        return result


    def set_last_id(self):
        if self.csv:
            with open(self.csv_path, 'r') as f:
                rows = []
                for line in f:
                    rows.append(line)
                last_id = rows[-1][0] # return first element (id) of last row

        elif self.db:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            ids = cur.execute("SELECT ID FROM trades;").fetchall()
            con.close()
            if len(ids) > 0:
                last_id = int(ids[-1][0]) # result is [(1,), (2,), (3,)] so we get last element of List, and then get the first element of that tuple
            else:
                last_id = 0
    
        else:
            last_id = 0

        self._counter = last_id

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
