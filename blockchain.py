from functools import reduce
import json
import requests

from wallet import Wallet
from utility.hash_util import hash_block
from utility.verification import Verification
from block import Block
from transaction import Transaction

MINING_REWARD = 10


class Blockchain:
    def __init__(self, public_key, node_id):
        genesis_block = Block(0, '', [], 0, 0)
        self.__chain = [genesis_block]
        self.__open_transactions = []
        self.__public_key = public_key
        self.node_id = node_id
        self.__peers_nodes = set()
        self.load_data()

    @property
    def hosting(self):
        return self.__public_key

    @hosting.setter
    def hosting(self, val):
        self.__public_key = val

    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, val):
        self.__chain = val

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def save_data(self):
        with open(f"blockchain-{self.node_id}.txt", mode='w') as f:
            savable_blockchain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash,
                                                                     [tx.__dict__ for tx in block_el.transactions],
                                                                     block_el.proof, block_el.time) for block_el
                                                               in self.__chain]]
            f.write(json.dumps(savable_blockchain))  # Ó json.dump(blockchain, f)
            f.write('\n')
            savable_transactions = [transaction.__dict__ for transaction in self.__open_transactions]
            f.write(json.dumps(savable_transactions))
            f.write('\n')
            f.write(json.dumps(list(self.__peers_nodes)))

    # file_content = pickle.loads(f.read())
    # blockchain = file_content['chain']
    # open_transactions = file_content['ot']

    def load_data(self):
        try:
            with open(f"blockchain-{self.node_id}.txt", mode='r') as f:
                file_content = f.readlines()
                self.chain = json.loads(file_content[0][:-1])
                self.__open_transactions = json.loads(file_content[1][:-1])
                updated_blockchain = []
                for block in self.__chain:
                    converted_transaction = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount'])
                                             for tx in block['transactions']]
                    updated_block = Block(
                        block['index'], block['previous_hash'], converted_transaction, block['proof'], block['time'])

                    updated_blockchain.append(updated_block)

                self.chain = updated_blockchain
                updated_transactions = []
                for tx in self.__open_transactions:
                    current_transaction = Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount'])
                    updated_transactions.append(current_transaction)
                self.__open_transactions = updated_transactions
                peer_nodes = json.loads(file_content[2])
                self.__peers_nodes = set(peer_nodes)
        except (IOError, IndexError):
            pass

    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self, sender=None):
        if sender is None:
            if self.__public_key is None:
                return None
            participant = self.__public_key
        else:
            participant = sender
        tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in self.__chain]
        open_tx_sender = [tx.amount for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        tx_receiver = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in
                       self.__chain]

        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_sender) > 0 else 0, tx_sender, 0)
        amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_receiver) > 0 else 0,
                                 tx_receiver, 0)
        return amount_received - amount_sent

    def add_transaction(self, sender, recipient, signature, amount=1.0, is_receiving=False):
        transaction = Transaction(sender, recipient, signature, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            if not is_receiving:
                for node in self.__peers_nodes:
                    url = f'http://{node}/broadcast-transaction'
                    try:
                        response = requests.post(url, json=transaction.__dict__)
                        if response.status_code == 500 or response.status_code == 400:
                            print('Transaction declined')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False

    def mine_block(self):
        if self.__public_key is None:
            return None
        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)

        proof = self.proof_of_work()

        transaction_reward = Transaction('MINING', self.__public_key, '', MINING_REWARD)
        copied_open_transactions = self.__open_transactions[:]
        for tx in copied_open_transactions:
            if not Wallet.verify_transaction(tx):
                return None
        copied_open_transactions.append(transaction_reward)
        block = Block(len(self.__chain), hashed_block, copied_open_transactions, proof)
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        for node in self.__peers_nodes:
            url = f'http://{node}/broadcast-block'
            converted_block = block.__dict__.copy()
            converted_block['transactions'] = [tx.__dict__ for tx in converted_block['transactions']]
            try:
                response = requests.post(url, json={'block': converted_block})
                if response.status_code == 500 or response.status_code == 400:
                    print('Block declined')

            except requests.exceptions.ConnectionError:
                continue
        return block

    def add_block(self, block):
        transactions = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount'])
                        for tx in block['transactions']]
        proof_is_valid = Verification.valid_proof(transactions[:-1], block['previous_hash'], block['proof'])
        hashes_match = hash_block(self.chain[-1]) == block['previous_hash']
        if not proof_is_valid or not hashes_match:
            return False
        converted_block = Block(block['index'], block['previous_hash'], transactions, block['proof'],
                                block['time'])
        self.__chain.append(converted_block)
        stored_transactions = self.__open_transactions[:]
        for itx in block['transactions']:
            for tx in stored_transactions:
                if itx == tx.__dict__:
                    try:
                        self.__open_transactions.remove(tx)
                    except ValueError:
                        print('Item was already removed')
        self.save_data()
        return True

    def add_peer_node(self, node):
        self.__peers_nodes.add(node)
        self.save_data()

    def remove_peer_nodes(self, node):
        self.__peers_nodes.discard(node)
        self.save_data()

    def get_all_nodes(self):
        return list(self.__peers_nodes)
# def get_last_value():
#   return self.chain[-1]
