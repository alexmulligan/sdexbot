# Python Code Snippets for the Stellar Network

## Keypair basics

```python
    from stellar_sdk import Keypair

    keypair = Keypair.from_secret('my_secret_key')
    public_key = keypair.public_key
    can_sign = keypair.can_sign()

    print(public_key)
    print(can_sign)
```

## Get transactions from account

```python
    from stellar_sdk import Server, Keypair

    server = Server(horizon_url="https://horizon.stellar.org")
    keypair = Keypair.from_secret('my_secret_key')
    public_key = keypair.public_key

    # get a list of transactions submitted by a particular account
    transactions = server.transactions().for_account(account_id=public_key).call()
    print(transactions)
```

## Listen for transactions and print them as they occur (stream)

    from stellar_sdk import Server, Keypair

    server = Server(horizon_url="https://horizon.stellar.org")
    keypair = Keypair.from_secret('my_secret_key')
    public_key = keypair.public_key
    last_cursor = 'now'  # or load where you left off


    def tx_handler(tx_response):
        print(tx_response)

    for tx in server.transactions().for_account(public_key).cursor(last_cursor).stream():
        tx_handler(tx)
```

## Send XLM for USDC (path payment; with memo)

```python
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
```

## Resolve Federation Address

```python
    from stellar_sdk.sep.federation import resolve_stellar_address

    record = resolve_stellar_address('alexmulligan*stellarterm.com', None, use_http=False)
    print("Public Address: " + record.account_id)
```

## Trade XLM/USDC

TODO: This is kind of messy; rewrite it so it's cleaner

```python
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
```

## Getting current price info

```python
    import requests

    tickers = requests.get('https://ticker.stellar.org/markets.json').json()
    data = {}
    for dict in tickers['pairs']:
        if dict['name'] == 'XLM_CENTUS':
            data = dict

    price = round(1/data['close'], 4)
    print('1 XLM = ' + str(price) + ' CENTUS')

## Get account balances with requests

```python
    import requests

    my_public_key = 'my_public_key'


    def get_balance(server: Server, public_key: str, asset_code: str) -> float:
        r = requests.get('https://horizon.stellar.org/accounts/' + public_key)
        balances = r.json()['balances']
        for bal in balances:
            if bal['asset_type'] == 'native':
                if asset_code == 'XLM':
                    return float(bal['balance'])

            else:
                if bal['asset_code'] == asset_code:
                    return float(bal['balances'])

## Getting account balances with stellar_sdk

```python
    from stellar_sdk import Server

    server = Server('https://horizon.stellar.org')
    my_public_key = 'my_public_key'


    def get_balance(server: Server, public_key: str, asset_code: str) -> float:
        account_call = server.accounts().account_id(public_key)
        balances = account_call.call()['balances']

        for bal in balances:
            if bal['asset_type'] == 'native':
                if asset_code == 'XLM':
                    return float(bal['balance'])

            else:
                if bal['asset_code'] == asset_code:
                    return float(bal['balance'])
```

## Get historical price data for SDEX pair

```python
    from stellar_sdk import Server, Network, Asset
    from datetime import datetime

    server = Server(horizon_url="https://horizon.stellar.org")

    xlm = Asset.native()
    usdc = Asset("USDC", "GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN")

    period = 3600000
    end = datetime.now()
    endTimestamp = round(end.timestamp()*1000) # convert seconds to milliseconds
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
```
