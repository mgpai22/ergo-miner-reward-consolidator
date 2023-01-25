import requests
import json
from decimal import Decimal


class WalletLockedError(Exception):
    def __init__(self, message):
        self.message = message


def send_from_node_wallet(node_address, api_key, address_to_send, value_in_nano_erg):
    headers = {
        'accept': 'application/json',
        'api_key': api_key,
        'Content-Type': 'application/json'
    }

    out = [
        {
            "address": address_to_send,
            "value": value_in_nano_erg,
            "assets": []
        }
    ]
    tx_id = requests.post(f'{node_address}/wallet/payment/send', headers=headers, data=json.dumps(out)).json()

    try:
        if tx_id['detail'][-16:] == "wallet is locked":
            raise WalletLockedError("wallet is locked")
    except TypeError as e:
        pass

    return tx_id


def unlock_wallet(node_address, api_key, password):
    headers = {
        "accept": "application/json",
        "api_key": api_key,
        "Content-Type": "application/json"
    }

    data = {"pass": password}

    return requests.post(f'{node_address}/wallet/unlock', headers=headers, data=json.dumps(data)).json()


def get_mining_address(node_address, api_key):
    headers = {
        "accept": "application/json",
        "api_key": api_key,
        "Content-Type": "application/json"
    }

    return requests.get(f"{node_address}/mining/rewardAddress", headers=headers).json()['rewardAddress']


def get_wallet_balance(address: str):
    return Decimal(
        requests.get(f"https://api-testnet.ergoplatform.com/api/v1/addresses/{address}/balance/confirmed").json()[
            'nanoErgs'])


def get_node_wallet_balance(node_address: str, api_key: str):
    headers = {
        "accept": "application/json",
        "api_key": api_key,
        "Content-Type": "application/json"
    }

    return Decimal(requests.get(f"{node_address}/wallet/balances", headers=headers).json()['balance'])
