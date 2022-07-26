from scripts.helpful_scripts import get_account
from brownie import interface,config,network
def main():
    get_weth()

def get_weth():
    """
    MINTS WETH by depositing ETH into the WETH contract 
    """
    # abi
    # address 
    account=get_account()
    weth = interface.IWeth(config['networks'][network.show_active()]['weth_token'])
    tx=weth.deposit({'from':account,"value":0.1 *10**18})
    tx.wait(1)
    print("received 0.1 weth")
    return tx
## now we have erc20 token that we can use to interact with aave application