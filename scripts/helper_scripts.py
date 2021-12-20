from brownie import network, config, accounts

LOCAL_BLOCKCHAIN_ENVIROMENTS = ["development", "ganache-local", "hardhat", "mainnet-fork"] 


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        print(accounts[0].balance())
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])
    #return None