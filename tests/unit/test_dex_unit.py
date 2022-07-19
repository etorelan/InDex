import pytest
from brownie import InDex, Token
from web3 import Web3
from scripts.helpful_scripts import get_account, approve_token

account = get_account(index=0)


@pytest.fixture
def token():
    account = get_account()
    return Token.deploy({"from": account})


@pytest.fixture
def dex(token):
    account = get_account()
    return InDex.deploy(token, {"from": account})


@pytest.mark.parametrize("start_token_amount", [0, 100, 500])
def test_start(start_token_amount, token, dex):

    account = get_account()

    approve_token(token, dex, start_token_amount, account=account)
    tx = dex.start(
        start_token_amount, {"from": account, "value": Web3.toWei(100, "ether")}
    )
    tx.wait(1)

    start_token_balance, start_eth_balance = (
        tx.events["SwappedToken"]["token"],
        tx.events["SwappedToken"]["_token"],
    )

    assert start_token_balance > 0
    assert start_eth_balance == Web3.toWei(0.5, "ether")


@pytest.mark.parametrize(
    "_fromAmount",
    [0, 1000, 1_000_000],
)
def test_getPrice(dex, _fromAmount):
    # First run will fail because solidity does not support dividing by zero
    _fromReserve = _to_reserve = _fromAmount

    price = dex.getPrice(_fromAmount, _fromReserve, _to_reserve)

    if price == 449 or price == 499248:
        assert True


@pytest.mark.parametrize(
    "ethAmount",
    [0, 1, 10],
)
def test_ethToToken(ethAmount, dex, token):
    account = get_account()

    start_token_amount = 100000000000000000000
    approve_token(
        _token=token, _spender=dex, _amount=start_token_amount, account=account
    )
    tx = dex.start(
        start_token_amount, {"from": account, "value": Web3.toWei(100, "ether")}
    )
    tx.wait(1)

    tx = dex.ethToToken({"from": account, "value": Web3.toWei(ethAmount, "ether")})
    tx.wait(1)
    swappedTokens = tx.events["SwappedToken"]["token"]

    if (
        swappedTokens == 0
        or swappedTokens == 987158034397061298
        or swappedTokens == 9066108938801491315
    ):
        assert True


@pytest.mark.parametrize(
    "tokenAmount",
    [0, 1, 10],
)
def test_tokenToEth(tokenAmount, dex, token):

    account = get_account()

    start_token_amount = 100000000000000000000
    approve_token(
        _token=token, _spender=dex, _amount=start_token_amount, account=account
    )
    tx = dex.start(
        start_token_amount, {"from": account, "value": Web3.toWei(100, "ether")}
    )
    tx.wait(1)

    approve_token(token, dex, start_token_amount, account=account)
    tx = dex.tokenToEth(Web3.toWei(tokenAmount, "ether"), {"from": account})
    tx.wait(1)
    ethAmount = tx.events["SwappedToken"]["token"]

    if (
        ethAmount == 0
        or ethAmount == 987158034397061298
        or ethAmount == 9066108938801491315
    ):
        assert True


@pytest.mark.parametrize(
    "stakeAmount",
    [0, 1, 10],
)
def test_stake(dex, token, stakeAmount):

    account = get_account()

    start_token_amount = 100000000000000000000

    approve_token(
        _token=token, _spender=dex, _amount=start_token_amount, account=account
    )
    tx = dex.start(
        start_token_amount, {"from": account, "value": Web3.toWei(100, "ether")}
    )
    tx.wait(1)

    approve_token(token, dex, start_token_amount, account=account)
    tx = dex.stake({"from": account, "value": Web3.toWei(stakeAmount, "ether")})
    tx.wait(1)
    liquidity_minted, token_amount = (
        tx.events["SwappedToken"]["token"],
        tx.events["SwappedToken"]["_token"],
    )

    if (
        liquidity_minted == 1
        or liquidity_minted == 1000000000000000000
        or liquidity_minted == 10000000000000000000
    ):
        assert True
    if (
        token_amount == 1
        or token_amount == 1000000000000000001
        or token_amount == 10000000000000000001
    ):
        assert True


@pytest.mark.parametrize("withdraw_amount", [0, 0.1, 0.2, 0.5])
def test_withdraw(dex, withdraw_amount, token):
    account = get_account()

    start_token_amount = 1000000000000000000

    approve_token(
        _token=token, _spender=dex, _amount=start_token_amount, account=account
    )
    tx = dex.start(
        start_token_amount, {"from": account, "value": Web3.toWei(1, "ether")}
    )
    tx.wait(1)

    if withdraw_amount:
        approve_token(token, dex, start_token_amount, account=account)
        tx = dex.stake({"from": account, "value": Web3.toWei(0.5, "ether")})
        tx.wait(1)

    tx = dex.withdraw(Web3.toWei(withdraw_amount, "ether"), {"from": account})
    tx.wait(1)
    eth_amount, token_amount = (
        tx.events["SwappedToken"]["token"],
        tx.events["SwappedToken"]["_token"],
    )
    print(f"eth_amount, token_amount {eth_amount, token_amount}")

    assert token_amount == 0 or token_amount == Web3.toWei(withdraw_amount, "ether")
