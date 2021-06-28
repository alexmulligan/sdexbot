from trader import Trader
from data_utils import *
from stellar_sdk import Server, Asset


def main():
    my_secret_key = input("Enter secret key: ").strip().upper()
    serv = Server('https://horizon.stellar.org')
    xlm = Asset.native()
    usdc = Asset('USDC', 'GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN')
    trader = Trader(serv, my_secret_key, usdc, xlm)

    running = True
    while running:
        user_input = input('\nPress enter to continue ').strip().lower()
        if user_input in ['break', 'exit', 'quit', 'stop', 'end']:
            break

        bids, asks = get_orders(trader)
        current_price = round(find_ask(asks, 0.01), 7)
        print(f'Submitting trade for {trader.base.code}-{trader.quote.code} at {round(1/current_price, 7)}')
        try:
            res = trader.sell_quote(0.01, current_price)
        except:
            res = {'successful': False}
        print('Trade Successful' if res['successful'] else 'Trade Failed')

if __name__ == '__main__':
    main()
