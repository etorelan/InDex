from brownie import InDex, Token
from web3 import Web3
from scripts.helpful_scripts import get_account


start_token_amount = 100000000000000000000


def deploy_and_start():
    account = get_account()
    token = Token.deploy({"from": account})
    dex = InDex.deploy(token, {"from": account})

    approve_token(token, dex, start_token_amount)
    start_tx = dex.start(
        start_token_amount,
        {"from": account, "value": Web3.toWei(100, "ether")},
    )
    start_tx.wait(1)
    print(
        start_tx.events["SwappedToken"]["token"],
        start_tx.events["SwappedToken"]["_token"],
    )
    return dex, token, account


def eth_to_token():
    dex, token, account = deploy_and_start()
    eth_token_swap = dex.ethToToken(
        {"from": account, "value": Web3.toWei(0.001, "ether")}
    )
    eth_token_swap.wait(1)
    tokens_gained = eth_token_swap.events["SwappedToken"]["token"]
    print("Eth has been swapped ♥")
    print(f"tokens_gained: {tokens_gained}")


def token_to_eth():
    dex, token, account = deploy_and_start()

    print(f"account balance: {account.balance()}")

    token_amount = 10
    approve_token(token, dex, token_amount)
    token_to_eth_swap = dex.tokenToEth(token_amount, {"from": account})
    token_to_eth_swap.wait(1)

    print(f"account balance: {account.balance()}")

    swapped_eth = token_to_eth_swap.events["SwappedToken"]["token"]
    print(f"swapped_eth: {swapped_eth}")


def stake():
    dex, token, account = deploy_and_start()

    print(f"account balance before stake: {account.balance()}")

    token_amount = 10000000000000000000000000
    approve_token(token, dex, token_amount)

    stake_tx = dex.stake({"from": account, "value": Web3.toWei(10, "ether")})
    stake_tx.wait(1)
    liquidity_minted = stake_tx.events["SwappedToken"]["token"]
    token_amount = stake_tx.events["SwappedToken"]["_token"]
    print(f"liquidity_minted, token_amount{liquidity_minted, token_amount}")


def stake_and_withdraw():
    dex, token, account = deploy_and_start()

    print(f"account balance before stake: {account.balance()}")

    token_amount = 10000000000000000000000000
    approve_token(token, dex, token_amount)

    stake_tx = dex.stake({"from": account, "value": Web3.toWei(10, "ether")})
    stake_tx.wait(1)
    liquidity_minted = stake_tx.events["SwappedToken"]["token"]
    token_amount = stake_tx.events["SwappedToken"]["_token"]
    print(f"liquidity_minted, token_amount{liquidity_minted, token_amount}")

    print(f"account balance before withdrawal: {account.balance()}")
    withdraw_tx = dex.withdraw(1, {"from": account})
    withdraw_tx.wait(1)
    print(f"account balance after withdrawal: {account.balance()}")

    eth_amount = withdraw_tx.events["SwappedToken"]["token"]
    token_amount = withdraw_tx.events["SwappedToken"]["_token"]
    print(f"eth and tokens gained: {eth_amount, token_amount}")


def approve_token(_token, _spender, _amount):
    print("Approving token transfer")
    tx = _token.approve(_spender, _amount)
    tx.wait(1)
    print("Token transfer approved")


def main():
    stake_and_withdraw()
