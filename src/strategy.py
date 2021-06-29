from trader import Trader
from data_utils import *
from stellar_sdk import Server, Asset

serv = Server('https://horizon.stellar.org')
usdc = Asset('USDC', 'GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN')
xlm = Asset.native()


def init():
    global trader

    my_secret_key = 'SCM45Q4IUWQTOPAQUAXNJN3NRFOHPTHJ2TCIVUQ7LSNKZMV6NNFK6B4Y'#input("Enter secret key: ").strip().upper()
    trader = Trader(serv, my_secret_key, xlm, usdc)


def main():
    init()

    # main loop - check ask/bid everytime orderbook updates
    in_market = False
    last_trade_price = 0
    last_bid = 0
    last_ask = 0
    for ob in serv.orderbook(trader.base, trader.quote).stream():
        bids, asks = get_orders(ob)
        spread = round((float(asks[0]['price']) / float(bids[0]['price'])), 7)
        if not in_market: # if not in the market - most recently "sold position in market" or sold XLM
            amount = find_amount(trader, 'quote')
            current_price = find_ask(asks, amount)

            if True:
                #res = trader.sell_quote(amount, current_price)
                print(f'sell_quote(amount={amount}, price={current_price})')
                last_trade_price = current_price
                last_ask = find_ask(asks, amount)
                last_bid = find_bid(bids, amount)
                in_market = True
                
        else: # if in the market - most recently "bought into the market" or bought XLM
            amount = find_amount(trader, 'base', reserve=3.5)
            current_price = find_bid(bids, amount)

            if current_price >= round(last_trade_price*1.0001, 7):
                #res = trader.sell_base(amount, current_price)
                print(f'sell_base(amount={amount}, price={current_price})')
                print(f'PROFIT: +{round(((current_price-last_trade_price)-1)*100, 4)}%\n')
                last_trade_price = current_price
                last_ask = find_ask(asks, amount)
                last_bid = find_bid(bids, amount)
                in_market = False
            elif current_price < last_bid:
                #res = trader.sell_base(amount, current_price)
                print(f'sell_base(amount={amount}, price={current_price})')
                print(f'LOSS: -{round((1-(current_price / last_trade_price))*100, 4)}%\n')
                last_trade_price = current_price
                last_ask = find_ask(asks, amount)
                last_bid = find_bid(bids, amount)
                in_market = False

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n')
