from stellar_sdk import Keypair, Asset, Server, Network, TransactionBuilder
from datetime import datetime

# TODO: implement methods to cancel trades (as long as they haven't been filled)
#       - to do this, I would probably need a function to query open offers and go from there to cancel them
#
# TODO: should an additional field with a link to the transaction on Horizon be logged? !!!IMPORTANT
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
            self.base.code, self.base.issuer, self.quote.code, self.quote.issuer, str(round(amount_base, 7)), str(round(1/price_in_quote, 7))
        ).set_timeout(self._YEAR).build()

        transaction.sign(self.keypair)
        response = self.server.submit_transaction(transaction)

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

        # TODO: handle reponse - check for success, etc.
        return response
