from stellar_sdk import Keypair, Asset, Server, Network, TransactionBuilder
from stellar_base import Address
from datetime import datetime
from logger import Logger

# TODO: implement methods to cancel trades (as long as they haven't been filled)
#       - this would require trade functions to return the offer_id and some way to check when orders have been filled.
#       - I could implement querying all open (unfilled) trades as well as checking a specific offer_id
#
# TODO: should any rounding on amount values and/or price be implemented? or should this be left to the program using the class
#       - also should the trade functions also return the purchased amount?
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
class Trader:
    _YEAR = 31536000

    def __init__(self, server: Server, secret_key: str, base_asset: Asset, quote_asset: Asset, enable_log: bool=True, log_type: str='all', log_id: int=None):
        """

        """
        self.server = server
        self.keypair = Keypair.from_secret(secret_key)
        self.account = server.load_account(account_id=self.keypair.public_key)
        self.address = Address(self.keypair.public_key, secret=None, network='public')

        self.base = base_asset
        self.baseData = self._get_asset_data(self.base)

        self.quote = quote_asset
        self.quoteData = self._get_asset_data(self.quote)

        self.log_enabled = enable_log
        if enable_log:
            self.logger = Logger(type=log_type, log_id=log_id)

    ############## Public Methods ###############

    # Shorter names for _place_trade functions
    def sell_base(self, amountBase: float, priceInQuote: float):
        return self._place_trade_base_to_quote(amountBase, priceInQuote)


    def buy_base(self, amountQuote: float, priceInQuote: float):
        return self._place_trade_quote_to_base(amountQuote, priceInQuote)

    
    def sell_quote(self, amountQuote: float, priceInQuote: float):
        return self._place_trade_quote_to_base(amountQuote, priceInQuote)


    def buy_quote(self, amountBase: float, priceInQuote: float):
        return self._place_trade_base_to_quote(amountBase, priceInQuote)


    def get_base_balance(self):
        return self._get_asset_balance(self.base)


    def get_quote_balance(self):
        return self._get_asset_balance(self.quote)

   ############## Private Methods ###############

    def _get_asset_data(self, asset: Asset):
        """

        """
        data = {'code': '', 'issuer': ''}

        if asset.is_native():
            data['code'] = 'XLM'
            data['issuer'] = None

        else:
            assetDict = asset.to_dict()
            data['code'] = assetDict['code']
            data['issuer'] = assetDict['issuer']

        return data


    def _get_asset_balance(self, asset: Asset):
        """

        """
        self.address.get()

        if asset.is_native():
            for record in self.address.balances:
                if record['asset_type'] == 'native':
                    return float(record['balance'])

        else:
            for record in self.address.balances:
                if record['asset_type'] != 'native':
                    if record['asset_code'] == asset.to_dict()['code']:
                        return float(record['balance'])


    def _place_trade_base_to_quote(self, amountBase: float, priceInQuote: float):
        """

        """
        transaction = TransactionBuilder(
            source_account=self.account, network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE, base_fee=100
        ).append_manage_sell_offer_op(
            self.baseData['code'], self.baseData['issuer'], self.quoteData['code'], self.quoteData['issuer'], str(amountBase), str(priceInQuote)
        ).set_timeout(self._YEAR).build()

        transaction.sign(self.keypair)
        response = self.server.submit_transaction(transaction)

        trade_data = {
            'timestamp': round(datetime.now().timestamp()),
            'action': 'SELL',
            'symbol': self.baseData['code'] + '-' + self.baseData['issuer'],
            'volume': round(amountBase / priceInQuote, 8), # results in amount in quote
            'currency': self.quoteData['code'], # TODO: fix this so it works for non-XLM quote assets
            'price': priceInQuote
        }
        if self.log_enabled:
            self.logger.log(trade_data)

        # TODO: handle reponse - check for success, etc.
        return response

    
    def _place_trade_quote_to_base(self, amountQuote: float, priceInQuote: float):
        """

        """

        priceInBase = round(1 / priceInQuote, 6) # calculate price in base since we're selling quote for base

        transaction = TransactionBuilder(
            source_account=self.account, network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE, base_fee=100
        ).append_manage_sell_offer_op(
            self.quoteData['code'], self.quoteData['issuer'], self.baseData['code'], self.baseData['issuer'], str(amountQuote), str(priceInBase)
        ).set_timeout(self._YEAR).build()

        transaction.sign(self.keypair)
        response = self.server.submit_transaction(transaction)

        trade_data = {
            'timestamp': round(datetime.now().timestamp()),
            'action': 'BUY',
            'symbol': self.baseData['code'] + '-' + self.baseData['issuer'],
            'volume': amountQuote,
            'currency': self.quoteData['code'], # TODO: fix this so it works for non-XLM quote assets
            'price': priceInQuote
        }
        if self.log_enabled:
            self.logger.log(trade_data)

        # TODO: handle reponse - check for success, etc.
        return response
