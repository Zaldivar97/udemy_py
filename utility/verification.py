from utility.hash_util import hash_block, hash_string_256
from wallet import Wallet


class Verification:

    @staticmethod
    def verify_transaction(transaction, get_balance):
        sender_balance = get_balance(transaction.sender)
        return sender_balance >= transaction.amount and Wallet.verify_transaction(transaction)

    @staticmethod
    def valid_proof(new_transactions, last_hash, proof):
        guess = (str([tx.to_ordered_dict() for tx in new_transactions]) + str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_256(guess)
        print(guess_hash)
        return guess_hash[0:2] == '00'

    @classmethod
    def verify_chain(cls, blockchain) -> bool:
        for i, block in enumerate(blockchain):
            if i == 0:
                continue
            if block.previous_hash != hash_block(blockchain[i - 1]):
                print('fail')
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print("WARNING: ¡INVALID BLOCKCHAIN!")
                return False
        return True


