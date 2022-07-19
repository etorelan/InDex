from brownie import accounts, network, config, interface

LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "development",
    "ganache",
    "hardhat",
    "local-ganache",
    "mainnet-fork",
]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    if network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])
    return None


def approve_token(_token, _spender, _amount, account):
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(_token)
    tx = erc20.approve(_spender, _amount, {"from": account})
    tx.wait(1)
    print("Approved!")
    return tx
