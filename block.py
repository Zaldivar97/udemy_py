from time import time
from utility.printable import Printable

from transaction import Transaction


class Block(Printable):
    def __init__(self, index, previous_hash, transactions, proof, timestamp=None):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.proof = proof
        self.time = time() if timestamp is None else timestamp

    # def __repr__(self):
    #   return f'Index: {self.index}, Previous_hash: {self.previous_hash}, Proof: {self.proof}'
    def object_to_dict(self):
        copied_block = self.__dict__.copy()
        copied_block['transactions'] = [tx.__dict__ for tx in copied_block['transactions']]

    @staticmethod
    def dict_to_object(block_dict, transactions=None):
        if transactions is None:
            converted_transactions = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount'])
                                      for tx in block_dict['transactions']]
        else:
            converted_transactions = transactions

        converted_block = Block(block_dict['index'], block_dict['previous_hash'], converted_transactions,
                                block_dict['proof'],
                                block_dict['time'])
        return converted_block
