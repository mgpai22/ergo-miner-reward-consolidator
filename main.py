import math
import time
from decimal import Decimal
from termcolor import colored

from api import send_from_node_wallet, WalletLockedError, unlock_wallet, get_mining_address, get_wallet_balance, \
    get_node_wallet_balance

MAX_ERG_PER_TX = 3000 # may go up to 5000

print(colored("Enter node ip:", "light_magenta"))
node_address = input()

if node_address[-1:] == '/':
    node_address = node_address[:-1]

print(colored("Enter node api key:", "light_magenta"))
api_key = input()

print(colored("Enter node wallet password (if pw is empty just hit enter) :", "light_magenta"))
password = input()

print(colored("Enter recipient address:", "light_magenta"))
recipient = input()

print(colored(f"node address: {node_address}", "red"))
print(colored(f"node api key: {api_key}", "red"))
print(colored(f"node wallet password: {password}", "red"))
print(colored(f"recipient: {recipient}", "red"))

print(colored("If any of this is wrong enter q to quit (hit enter to skip) :", "red"))

exit = input()

if exit.lower() == "q":
    quit(0)

mining_address = get_mining_address(node_address, api_key)
balance = get_wallet_balance(mining_address)
node_balance = get_node_wallet_balance(node_address, api_key)

print(colored(f"Mining Address is: {mining_address}", "light_magenta"))

print(colored(f"Mining Address Balance: {balance * Decimal('1e-9')} ERG", "light_magenta"))

print(colored(f"Node Balance: {node_balance * Decimal('1e-9')} ERG", "light_magenta"))

print(colored("Enter amount of ERG to transfer (hit enter for all mining balance):", "red"))

amount_to_send = input() or 0

if amount_to_send != 0:
    try:
        if float(amount_to_send) < 1:
            res = send_from_node_wallet(node_address, api_key, recipient,
                                        int((Decimal(amount_to_send) * Decimal('1e9'))))
            print(colored(f"tx hash: {res}", "light_magenta"))
            quit(0)
    except Exception as e:
        print(e)
        pass
    amount_to_send = Decimal(int(amount_to_send) * math.pow(10, 9))
else:
    amount_to_send = balance

times_to_run = math.floor(amount_to_send / Decimal(MAX_ERG_PER_TX * 10 ** 9))

remainder_ergs = amount_to_send % Decimal(MAX_ERG_PER_TX * 10 ** 9)

if remainder_ergs == 0:
    tx_amount = times_to_run
else:
    tx_amount = times_to_run + 1

print(colored(f"Note that {tx_amount} transactions will be sent", "red"))

if times_to_run == 0:
    times_to_run = 1

for x in range(times_to_run):
    while True:
        try:
            if amount_to_send < int(MAX_ERG_PER_TX * math.pow(10, 9)):
                res = send_from_node_wallet(node_address, api_key, recipient, int(amount_to_send))
                print(colored(f"tx hash: {res}", "light_magenta"))
                quit(0)
            res = send_from_node_wallet(node_address, api_key, recipient, int(MAX_ERG_PER_TX * math.pow(10, 9)))
            print(colored(f"tx hash: {res}", "light_magenta"))
            break
        except WalletLockedError as e:
            print("wallet is locked attempting to unlock")
            unlock_wallet(node_address, api_key, password)
            print("wallet unlocked")

        except Exception as e:
            print(e)

        time.sleep(5)

if remainder_ergs > 1000000:
    while True:
        try:
            res = send_from_node_wallet(node_address, api_key, recipient, int(remainder_ergs))
            print(colored(f"tx hash: {res}", "light_magenta"))
            quit(0)
        except WalletLockedError as e:
            print("wallet is locked attempting to unlock")
            unlock_wallet(node_address, api_key, password)
            print("wallet unlocked")

        except Exception as e:
            print(e)

        time.sleep(5)
