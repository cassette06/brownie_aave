from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from brownie import config,network,interface
from web3 import Web3
amount=Web3.toWei(0.1,'ether')
def main():
    account=get_account()
    print(f'the eth amount of account is {account.balance()}')
    erc20_address=config['networks'][network.show_active()]['weth_token']
    if network.show_active() in ['mainnet-fork-dev']:
        get_weth()
    
    lending_pool=get_lending_pool()
    print(lending_pool)
    # you need to approve another contract to use your token.
    # erc20 token has the approve function making sure that whenever we 
    # send a token to someone or whenever a token calls a function that uses
    # our tokens we actually have given them permission to do so
    # Approve sending out ERC20 token
    approve_erc20(amount,lending_pool.address,erc20_address,account)
    print('Depositing...')
    tx=lending_pool.deposit(erc20_address, amount, account.address, 0,{'from':account})
    tx.wait(1)
    print('Deposited!')
    print(f'the eth amount of account is {account.balance()}')
    bororrowable_eth,total_debt,total_colleteral=get_borrowable_data(lending_pool,account)
    print('lets borrow!')
    # DAI in terms of ETH
    dai_eth_price = get_asset_price(
        config['networks'][network.show_active()]['dai_eth_price_feed'])
    amount_dai_to_borrow =(1/dai_eth_price ) *(bororrowable_eth *0.95)
    print(f'we are going to borrow {amount_dai_to_borrow} DAI')
    # now we will borrow!
    dai_address=config['networks'][network.show_active()]['dai_token']
    borrow_tx=lending_pool.borrow(dai_address,
    Web3.toWei(amount_dai_to_borrow,'ether'), 1,0,account.address,{'from':account} )
    borrow_tx.wait(1)
    print('we have borrowed some DAI!!!')
    print(f'the eth amount of account is {account.balance()}')
    get_borrowable_data(lending_pool,account)
    repay_all(Web3.toWei(amount_dai_to_borrow,'ether'),lending_pool,account)
    bororrowable_eth,total_debt,total_colleteral=get_borrowable_data(lending_pool,account)
    # withdraw
    withdraw_amount(lending_pool,Web3.toWei(total_colleteral*0.95,"ether"),account)
    print('withdrawed!')
    get_borrowable_data(lending_pool,account)

    print('starting withdrawing the weth')
    weth = interface.IWeth(config['networks'][network.show_active()]['weth_token'])
    tx=weth.withdraw(total_colleteral*0.8 *10**18,{'from':account})
    tx.wait(1)
   
    print(f'the eth amount of account is {account.balance()}')


def withdraw_amount(lending_pool,amount,account):
    # approve_erc20(Web3.toWei(amount,'ether'),lending_pool.address,
    # config['networks'][network.show_active()]['weth_token'],
    # account)
    tx=lending_pool.withdraw(config['networks'][network.show_active()]['weth_token'],amount,account.address,{"from":account})
    tx.wait(1)

def repay_all(amount,lending_pool,account):
    approve_erc20(Web3.toWei(amount,'ether'),lending_pool.address,
    config['networks'][network.show_active()]['dai_token'],
    account)
    repay_tx=lending_pool.repay(config['networks'][network.show_active()]['dai_token'],
    amount, 1,account.address,{'from':account})
    repay_tx.wait(1)
    print('repaid!')
    print(f'the eth amount of account is {account.balance()}')

def get_asset_price(price_feed_address):
    dai_eth_price_feed=interface.AggregatorV3Interface(price_feed_address)
    latest_price=dai_eth_price_feed.latestRoundData()[1]
    converted_latest_price=Web3.fromWei(latest_price,'ether')
    print(f'the DAI/ETH price is {converted_latest_price}')
    return float(converted_latest_price)


def get_borrowable_data(lending_pool,account):
    (total_collateral_eth,total_debt_eth,availbale_borrow_eth,current_liquidation_threshold,ltv,health_factor)=lending_pool.getUserAccountData(account.address)
    availbale_borrow_eth=Web3.fromWei(availbale_borrow_eth,'ether')
    total_collateral_eth=Web3.fromWei(total_collateral_eth,'ether')
    total_debt_eth=Web3.fromWei(total_collateral_eth,'ether')
    print(f"you have {total_collateral_eth}worth of ETH deposited.")
    print(f"you have {total_debt_eth}worth of ETH borrowed.")
    print(f"you can borrow {availbale_borrow_eth}worth of ETH.")
    return (float(availbale_borrow_eth),float(total_debt_eth),float(total_collateral_eth))



def approve_erc20(amount,spender,erc20_address,account):
    print("Approving erc20 token...")
    erc20=interface.IERC20(erc20_address)
    tx=erc20.approve(spender,amount,{'from':account})
    tx.wait(1)
    print('Approved!')
    return tx

def get_lending_pool():
    lending_pool_addresses_provider=interface.ILendingPoolAddressesProvider(
        config['networks'][network.show_active()]['lending_pool_addresses_provider'])
    lending_pool_address=lending_pool_addresses_provider.getLendingPool()

    lending_pool=interface.ILendingPool(lending_pool_address)
    return lending_pool