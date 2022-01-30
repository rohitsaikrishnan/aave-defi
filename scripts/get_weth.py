from scripts.helpful_scripts import get_account
from brownie import interface, config, network
def main():
    get_weth()

def get_weth():
    """
    mints WETH by depositing ETH
    :return:
    """
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth-address"])
    tx = weth.deposit({"from": account, "value": 1 * 10 ** 18})
    print(f"Received 0.1 ETH")
    tx.wait(1)
    return tx


