from stellar_sdk import Keypair, Asset, Server, Network, TransactionBuilder
from datetime import datetime

# TODO: implement methods to cancel trades (as long as they haven't been filled)
#       - this would require trade functions to return the offer_id and some way to check when orders have been filled.
#       - I could implement querying all open (unfilled) trades as well as checking a specific offer_id
#
# TODO: should any rounding on amount values and/or price be implemented? or should this be left to the program using the class
# ANSWER: I'm pretty sure Stellar rounds their values to 7 decimals.  So I think I want everything to be rounded in this class
#
# TODO: idea to cover (most) of ^: integrate with the logging to return a unique trade id (locally generated)
#       - this could be used to check if the order is filled, cancel if it is unfilled, and lookup the trade in the database/log
#       - the Trader object would also have a lastTradeId attribute which is the trade id of the last trade placed
#       - querying a trade by the trade id should also be able to provide amount, price, time, etc. either/both from stellar and the database/log
#
# TODO: instead of logging a trade as soon as the order is placed, log it when it is filled for a more accurate timestamp
#       - this goes hand in hand with being able to check/listen for when orders are filled
#
# TODO: should an additional field with a link to the transaction on Horizon be logged?
#
# NOTE: I don't think most of these ^ suggested solutions are what I want to do anymore.  I do think that some type of order_id could be used to track/cancel orders,
#       but what if an order is partially filled? And I want to keep logging completely separate. Like have a program listen to my bot account for filled trades
#
class Trader:
    _YEAR = 31536000

    def __init__(self, server: Server, secret_key: str, base_asset: Asset, quote_asset: Asset):
        self.server = server
        self.keypair = Keypair.from_secret(secret_key)
        self.account = server.load_account(account_id=self.keypair.public_key)
        self.base = base_asset
        self.quote = quote_asset

    ############## Public Methods ###############

    # Shorter names for _place_trade functions
    def sell_base(self, amount_base: float, price_in_quote: float):
        return self._place_trade_base_to_quote(amount_base, price_in_quote)


    def buy_base(self, amount_quote: float, price_in_quote: float):
        return self._place_trade_quote_to_base(amount_quote, price_in_quote)

    
    def sell_quote(self, amount_quote: float, price_in_quote: float):
        return self._place_trade_quote_to_base(amount_quote, price_in_quote)


    def buy_quote(self, amount_base: float, price_in_quote: float):
        return self._place_trade_base_to_quote(amount_base, price_in_quote)


    def get_base_balance(self) -> float:
        return self._get_asset_balance(self.base)


    def get_quote_balance(self) -> float:
        return self._get_asset_balance(self.quote)

   ############## Private Methods ###############

    def _get_asset_balance(self, asset: Asset) -> float:
        account_call = self.server.accounts().account_id(self.keypair.public_key)
        balances = account_call.call()['balances']

        for bal in balances:
            if bal['asset_type'] == 'native':
                if asset.is_native():
                    return float(bal['balance'])

            else:
                if bal['asset_code'] == asset.code:
                    return float(bal['balance'])


    def _place_trade_base_to_quote(self, amount_base: float, price_in_quote: float):
        transaction = TransactionBuilder(
            source_account=self.account, network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE, base_fee=100
        ).append_manage_sell_offer_op(
            self.base.code, self.base.issuer, self.quote.code, self.quote.issuer, str(round(amount_base, 7)), str(round(price_in_quote, 7))
        ).set_timeout(self._YEAR).build()

        transaction.sign(self.keypair)
        response = self.server.submit_transaction(transaction)

        '''trade_data = {
            'timestamp': round(datetime.now().timestamp()),
            'action': 'SELL',
            'symbol': self.base.code + '-' + self.base.issuer,
            'volume': round(amount_base / price_in_quote, 7), # results in amount in quote
            'currency': self.quote.code if self.quote.is_native() else self.quote.code + '-' + self.quote.issuer,
            'price': price_in_quote
        }''' # might still need to use this, so leaving it in

        # TODO: handle reponse - check for success, etc.
        return response

    
    def _place_trade_quote_to_base(self, amount_quote: float, price_in_quote: float):

        price_in_base = round(1 / price_in_quote, 7) # calculate price in base since we're selling quote for base

        transaction = TransactionBuilder(
            source_account=self.account, network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE, base_fee=100
        ).append_manage_sell_offer_op(
            self.quote.code, self.quote.issuer, self.base.code, self.base.issuer, str(round(amount_quote, 7)), str(price_in_base)
        ).set_timeout(self._YEAR).build()

        transaction.sign(self.keypair)
        response = self.server.submit_transaction(transaction)

        '''trade_data = {
            'timestamp': round(datetime.now().timestamp()),
            'action': 'BUY',
            'symbol': self.base.code + '-' + self.base.issuer,
            'volume': amount_quote,
            'currency': self.quote.code if self.quote.is_native() else self.quote.code + '-' + self.quote.issuer,
            'price': price_in_quote
        }'''  # might still need to use this, so leaving it in

        # TODO: handle reponse - check for success, etc.
        return response
