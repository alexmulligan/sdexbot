# Python Code Snippets for the Stellar Network

## Keypair basics

    from stellar_sdk import Keypair

    keypair = Keypair.from_secret('my_secret_key')
    public_key = keypair.public_key
    can_sign = keypair.can_sign()

    print(public_key)
    print(can_sign)

## Get transactions from account

    from stellar_sdk import Server, Keypair

    server = Server(horizon_url="https://horizon.stellar.org")
    keypair = Keypair.from_secret('my_secret_key')
    public_key = keypair.public_key

    # get a list of transactions submitted by a particular account
    transactions = server.transactions().for_account(account_id=public_key).call()
    print(transactions)

## Listen for transactions and print them as they occur (stream)

This could be used for handling output and database logging of transactions made by bot

    from stellar_sdk import Server, Keypair

    server = Server(horizon_url="https://horizon.stellar.org")
    keypair = Keypair.from_secret('my_secret_key')
    public_key = keypair.public_key
    last_cursor = 'now'  # or load where you left off


    # Get all transactions from account - for past transactions, not for occurring ones
    #transactions = server.transactions().for_account(account_id=public_key).call()
    #print(transactions)


    def tx_handler(tx_response):
        print(tx_response)

    for tx in server.transactions().for_account(public_key).cursor(last_cursor).stream():
        tx_handler(tx)

## Send XLM for USDC (path payment; with memo)

    from stellar_sdk import Keypair, Server, TransactionBuilder, Network, Asset

    server = Server(horizon_url="https://horizon.stellar.org")
    keypair = Keypair.from_secret('my_secret_key')
    public_key = keypair.public_key
    account = server.load_account(account_id=public_key)

    path = [
        Asset.native(),
        Asset("USDC", "GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN")
    ]

    transaction = TransactionBuilder(
        source_account=account, network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE, base_fee=100
    ).add_text_memo("Test Memo").append_path_payment_strict_receive_op(
        destination=public_key, send_code="XLM", send_issuer=None, send_max="0.3", dest_code="USDC", dest_issuer="GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN", dest_amount="0.15", path=path
    ).set_timeout(30).build()

    transaction.sign(keypair)
    response = server.submit_transaction(transaction)

## Resolve Federation Address

    from stellar_sdk.sep.federation import resolve_stellar_address

    record = resolve_stellar_address('alexmulligan*stellarterm.com', None, use_http=False)
    print("Public Address: " + record.account_id)

## Trade XLM/USDC

    from stellar_sdk import Keypair, Server, TransactionBuilder, Network, Asset

    server = Server(horizon_url="https://horizon.stellar.org")
    keypair = Keypair.from_secret('my_secret_key')
    public_key = keypair.public_key
    account = server.load_account(account_id=public_key)

    xlm = Asset.native().to_dict()
    usdc = Asset("USDC", "GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN").to_dict()


    def tradeXLMtoUSDC(amtXLM: str, priceInUSDC: str):
        transaction = TransactionBuilder(
            source_account=account, network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE, base_fee=100
        ).append_manage_sell_offer_op(
            'XLM', None, usdc['code'], usdc['issuer'], amtXLM, price, 0
        ).set_timeout(60).build()

        transaction.sign(keypair)
        response = server.submit_transaction(transaction)
        return response


    def tradeUSDCtoXLM(amtUSDC: str, priceInXLM: str):
        transaction = TransactionBuilder(
            source_account=account, network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE
        ).append_manage_sell_offer_op(
            usdc['code'], usdc['issuer'], 'XLM', None, amtUSDC, price, 0
        ).set_timeout(60).build()

        transaction.sign(keypair)
        response = server.submit_transaction(transaction)
        return response

    #tradeXLMtoUSDC('2', '0.65')
    #tradeUSDCtoXLM('1.337', '1.51')

## Getting price info

    import requests

    tickers = requests.get('https://ticker.stellar.org/markets.json').json()
    data = {}
    for dict in tickers['pairs']:
        if dict['name'] == 'XLM_CENTUS':
            data = dict

    price = round(1/data['close'], 4)
    print('1 XLM = ' + str(price) + ' CENTUS')

## Get all account balances (request)

    import requests
    from time import sleep

    def get_balance(account):
        r = requests.get(base_url + '/accounts/' + accounts[account]['address'])
        if r.status_code == 200:
            balances = r.json()
            balances = balances.get('balances', [])
            for b in balances:
                asset = b.get('asset_type')
                if asset == 'native':
                    print('{} XLM'.format(b.get('balance')))
                else:
                    print('{} {} - issuer: {}'.format(b.get('balance'), b.get('asset_code'), b.get('asset_issuer')))
        else:
            print('Account not found')

## Alternative get account balances (sdk)

    from stellar_base import Address

    address = Address(address=pub_key, secret=None, network='public')

    address.get()

    for asset in address.balances:
        if asset['asset_type'] == 'native':
            print('XLM: ' + asset['balance'])

        else:
            print(asset['asset_code'] + ': ' + asset['balance'])

## Get historical price data for SDEX pair

    from stellar_sdk import Server, Network, Asset
    from datetime import datetime

    server = Server(horizon_url="https://horizon.stellar.org")

    xlm = Asset.native()
    usdc = Asset("USDC", "GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN")

    period = 3600000
    end = datetime.now()
    endTimestamp = round(end.timestamp()*1000)
    start = datetime(end.year, end.month, end.day-4, end.hour, end.minute, end.second)
    startTimestamp = round(start.timestamp()*1000)

    data = []
    records = server.trade_aggregations(xlm, usdc, period, startTimestamp, endTimestamp, 0).cursor('now')

    curr = records.call()
    while curr['_embedded']['records'] != []:
        for record in curr['_embedded']['records']:
            data.append(record['close'])

        curr = records.next()

    print(data)
