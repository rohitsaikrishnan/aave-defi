from scripts.helpful_scripts import get_account
from brownie import network, config, interface
from scripts.get_weth import get_weth
from web3 import Web3

AMOUNT = Web3.toWei(0.05, "ether")

def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth-address"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()

    lending_pool = get_lending_pool()
    approve_erc20(AMOUNT, lending_pool.address, erc20_address, account)
    erc20_contract = interface.IERC20(
        erc20_address
    )
    balance = erc20_contract.balanceOf(account.address)
    print(f'balance is {balance}')
    print(AMOUNT)
    tx = lending_pool.deposit(erc20_address, AMOUNT, account.address, 0, {"from": account})
    tx.wait(1)
    print("Deposited!")
    borrowable_eth, total_debt_eth = get_borrowable_data(lending_pool, account)
    print("Let's Borrow!")
    dai_eth_price_feed = get_asset_price(config["networks"][network.show_active()]["dai_eth_price_feed"])
    amount_dai_to_borrow = (1 / dai_eth_price_feed) * (borrowable_eth * 0.95)
    print(f"We are going to borrow {amount_dai_to_borrow} DAI")
    dai_address = config["networks"][network.show_active()]["dai_token"]

    borrow_txn = lending_pool.borrow(dai_address, Web3.toWei(120, "ether"), 1, 0, account.address, {"from":account})
    borrow_txn.wait(1)
    print("We borrowed some DAI!")
    get_borrowable_data(lending_pool, account)
    repay_all(120, lending_pool, account)
    get_borrowable_data(lending_pool, account)

def repay_all(amount, lending_pool, account):
    approve_erc20(Web3.toWei(amount, "ether"), lending_pool.address, config["networks"][network.show_active()]["dai_token"], account)
    repay_tx = lending_pool.repay(config["networks"][network.show_active()]["dai_token"], Web3.toWei(amount, "ether"), 1, account.address, {"from":account})
    repay_tx.wait(1)
    print("Repayed!")


def get_asset_price(price_feed_address):
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price,"ether")
    print(f"The DAI/ETH price is {converted_latest_price}")
    return float(converted_latest_price)




def get_borrowable_data(lending_pool, account):
    (total_collateral_eth, total_debt_eth, available_borrow_eth, current_liquidation_threshold, ltv, health_facor) = \
        lending_pool.getUserAccountData(account.address)
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"You have {total_collateral_eth} worth of ETH deposited.")
    print(f"You have {total_debt_eth} worth of ETH borrowed.")
    print(f"You can borrow {available_borrow_eth} worth of ETH.")
    return (float(available_borrow_eth), float(total_debt_eth))


def approve_erc20(amount, spender, erc20_address, account):
    print("Approving!")
    erc20_contract = interface.IERC20(
        erc20_address
    )
    tx = erc20_contract.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("approved!")



def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )

    lending_pool_address = lending_pool_addresses_provider.getLendingPool()

    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


