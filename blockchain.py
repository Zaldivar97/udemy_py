from functools import reduce
import json

from hash_util import hash_block
from verification import Verification
from block import Block
from transaction import Transaction
import pickle

MINING_REWARD = 10


class Blockchain:
    def __init__(self, hosting_node_id):
        genesis_block = Block(0, '', [], 0, 0)
        self.__chain = [genesis_block]
        self.__open_transactions = []
        self.load_data()
        self.hosting = hosting_node_id

    def get_chain(self):
        return self.__chain[:]

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def save_data(self):
        with open('blockchain.txt', mode='w') as f:
            saveable_blockchain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash,
                                                                      [tx.__dict__ for tx in block_el.transactions],
                                                                      block_el.proof, block_el.time) for block_el
                                                                in self.__chain]]
            f.write(json.dumps(saveable_blockchain))  # Ó json.dump(blockchain, f)
            f.write('\n')
            savable_transactions = [transaction.__dict__ for transaction in self.__open_transactions]
            f.write(json.dumps(savable_transactions))

    # file_content = pickle.loads(f.read())
    # blockchain = file_content['chain']
    # open_transactions = file_content['ot']

    def load_data(self):
        try:
            with open('blockchain.txt', mode='r') as f:
                file_content = f.readlines()
                self.__chain = json.loads(file_content[0][:-1])
                self.__open_transactions = json.loads(file_content[1])
                updated_blockchain = []
                for block in self.__chain:
                    converted_transaction = [Transaction(tx['sender'], tx['recipient'], tx['amount'])
                                             for tx in block['transactions']]
                    updated_block = Block(
                        block['index'], block['previous_hash'], converted_transaction, block['proof'], block['time'])

                    updated_blockchain.append(updated_block)

                self.__chain = updated_blockchain
                updated_transactions = []
                for tx in self.__open_transactions:
                    current_transaction = Transaction(tx['sender'], tx['recipient'], tx['amount'])
                    updated_transactions.append(current_transaction)
                self.__open_transactions = updated_transactions
        except (IOError, IndexError):
            pass

    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self):
        tx_sender = [[tx.amount for tx in block.transactions if tx.sender == self.hosting] for block in self.__chain]
        open_tx_sender = [tx.amount for tx in self.__open_transactions if tx.sender == self.hosting]
        tx_sender.append(open_tx_sender)
        tx_receiver = [[tx.amount for tx in block.transactions if tx.recipient == self.hosting] for block in
                       self.__chain]

        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_sender) > 0 else 0, tx_sender, 0)
        amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_receiver) > 0 else 0,
                                 tx_receiver, 0)
        return amount_received - amount_sent

    def add_transaction(self, recipient, sender, amount=1.0):
        transaction = Transaction(sender, recipient, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    def mine_block(self):
        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)

        proof = self.proof_of_work()

        transaction_reward = Transaction('MINING', self.hosting, MINING_REWARD)
        copied_open_transactions = self.__open_transactions[:]
        copied_open_transactions.append(transaction_reward)
        block = Block(len(self.__chain), hashed_block, copied_open_transactions, proof)
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        return True

#def get_last_value():
 #   return self.chain[-1]









