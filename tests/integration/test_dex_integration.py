from brownie import InDex, Token
from web3 import Web3
from scripts.helpful_scripts import get_account

start_token_amount = 100000000000000000000


def test_dex_integration():
    account = get_account()
    token = Token.deploy({"from": account})
    dex = InDex.deploy(token, {"from": account})

    approve_token(token, dex, start_token_amount, account=account)
    start_tx = dex.start(
        start_token_amount,
        {"from": account, "value": Web3.toWei(100, "ether")},  # 900
    )
    start_tx.wait(1)

    eth_token_swap = dex.ethToToken(
        {"from": account, "value": Web3.toWei(1, "ether")}  # 899
    )
    eth_token_swap.wait(1)

    token_amount = 1000000000000000000
    approve_token(token, dex, token_amount, account=account)
    token_to_eth_swap = dex.tokenToEth(token_amount, {"from": account})  # 900
    token_to_eth_swap.wait(1)

    token_amount = 10000000000000000000000000000
    approve_token(token, dex, token_amount, account=account)
    deposit_tx = dex.stake({"from": account, "value": Web3.toWei(10, "ether")})  # 890
    deposit_tx.wait(1)

    withdraw_tx = dex.withdraw(Web3.toWei(1, "ether"), {"from": account})  # 891
    withdraw_tx.wait(1)

    assert str(account.balance())[0:3] == str(1000 - 100 - 1 + 1 - 10 + 1)


def approve_token(_token, _spender, _amount, account):
    print("Approving token transfer")
    tx = _token.approve(_spender, _amount, {"from": account})
    tx.wait(1)
    print("Token transfer approved")
