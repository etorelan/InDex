from brownie import InDex, Token
from web3 import Web3
from scripts.helpful_scripts import get_account, approve_token

start_token_amount = 500000000000000000


def main():
    account = get_account()
    token = Token.deploy({"from": account})
    dex = InDex.deploy(token, {"from": account})

    approve_token(token, dex, start_token_amount, account=account)
    tx = dex.start(
        start_token_amount, {"from": account, "value": Web3.toWei(0.5, "ether")}
    )
    tx.wait(1)

    price = dex.getPrice(1000, 1_000_000, 1_000_000)
    print(f"Price: {price}")

    tx = dex.ethToToken({"from": account, "value": Web3.toWei(0.01, "ether")})
    tx.wait(1)
    tokenAmount = tx.events["SwappedToken"]["token"]
    print(f"tokenAmount: {tokenAmount}")
    print("ETH has been swapped")

    approve_token(token, dex, start_token_amount, account=account)
    tx = dex.tokenToEth(Web3.toWei(0.01, "ether"), {"from": account})
    tx.wait(1)
    ethAmount = tx.events["SwappedToken"]["token"]
    print(f"ethAmount: {ethAmount}")

    approve_token(token, dex, start_token_amount, account=account)
    tx = dex.stake({"from": account, "value": Web3.toWei(0.01, "ether")})
    tx.wait(1)
    liquidity_minted, token_amount = (
        tx.events["SwappedToken"]["token"],
        tx.events["SwappedToken"]["_token"],
    )
    print(f"liquidity_minted, token_amount: {liquidity_minted, token_amount}")

    withdrawAmount = dex.getWithdrawAmount({"from": account})
    print(f"withdrawAmount: {withdrawAmount}")

    tx = dex.withdraw(withdrawAmount, {"from": account})
    tx.wait(1)
    eth_amount, token_amount = (
        tx.events["SwappedToken"]["token"],
        tx.events["SwappedToken"]["_token"],
    )
    print(f"eth_amount, token_amount: {eth_amount, token_amount}")
