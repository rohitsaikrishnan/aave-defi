from brownie import network, accounts,config

LOCAL_BLOCKCHAIN_ENV = ["ganache-local", "development"]
FORKED_LOCAL_ENV = ["mainnet-fork", "mainnet-fork-dev"]

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (network.show_active() in LOCAL_BLOCKCHAIN_ENV) or (network.show_active() in FORKED_LOCAL_ENV):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])