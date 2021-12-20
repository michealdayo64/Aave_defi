from brownie import config, network, interface 
from scripts.helper_scripts import get_account
from scripts.get_weth import get_weth
from web3 import Web3

# 0.1
amount = Web3.toWei(0.1, "ether")

def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    lending_pool = get_lending_pool()
    #print(lending_pool)
    # Approve sending out ERC20 tokens
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    tx = lending_pool.deposit(erc20_address, amount, account.address, 0,  {"from": account})
    print("Depositing")
    tx.wait(1)
    print("Deposited")
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"])
    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    # borrowable_eth -> borrowable_dai * 95%
    print(f"we are going to borrow {amount_dai_to_borrow} Dai")
    # Now we will borrow
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_address, 
        Web3.toWei(amount_dai_to_borrow, "ether"), 
        1,
        0,
        account.address,
        {"from": account}
        )
    borrow_tx.wait(1)
    print("We borrowed some DAI")
    get_borrowable_data(lending_pool, account)
    repay_all(amount, lending_pool, account)
    print("You just deposted, borrowed, and repayed with Aave, Brownie, and Chainlink")

def repay_all(amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool, 
        config["networks"][network.show_active()]["dai_token"], 
        account)
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"], 
        amount,
        1,
        account.address,
        {"from": account}
    )
    repay_tx.wait(1)
    print("Repayed")

def get_asset_price(price_feed_address):
    dai_eth_price_feed = interface.IAggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    convert_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"The DAI/ETH price is {convert_latest_price}")
    return float(convert_latest_price)

def get_borrowable_data(lending_pool, account):
    ( totalCollateralETH,
      totalDebtETH,
      availableBorrowsETH,
      currentLiquidationThreshold,
      ltv,
      healthFactor) = lending_pool.getUserAccountData(account.address)
    availableBorrowsETH = Web3.fromWei(availableBorrowsETH, "ether")
    totalCollateralETH = Web3.fromWei(totalCollateralETH, "ether")
    totalDebtETH = Web3.fromWei(totalCollateralETH, "ether")
    print(f"You have {totalCollateralETH} worth of ETH deposited.")
    print(f"you have {totalDebtETH} worth of ETH borrowed")
    print(f"You can borrow {availableBorrowsETH} worth of ETH")
    return(float(availableBorrowsETH), float(totalDebtETH))

def approve_erc20(amount, spender, erc20_address, account):
    #ABI
    #Address
    print("Approving Tranaction")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved")
    return tx


def get_lending_pool():
    #ABI
    #Address 
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool