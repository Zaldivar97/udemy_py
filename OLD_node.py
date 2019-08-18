from utility.verification import Verification
from blockchain import Blockchain
from wallet import Wallet


class Node:
    def __init__(self):
        # self.id = str(uuid4())
        self.wallet = Wallet()
        self.wallet.create_keys()
        self.blockchain = Blockchain(self.wallet.public_key)

    def get_transaction_values(self):
        recipient = input("Recipient:")
        amount = input("Amount:")
        return recipient, amount

    def get_user_choice(self):
        choice = input('Enter an option: ')
        return choice

    def print_blockchain_elements(self):
        if len(self.blockchain.chain) > 0:
            for block in self.blockchain.chain:
                print(block)
        else:
            print("There's no blocks")

    def listen_for_input(self):
        waiting_for_input = True
        while waiting_for_input:

            print("Please choose:")
            print("1. Add a new transaction value")
            print("2. Mine a new block")
            print("3. Output the blockchain blocks")
            print("4. Create wallet")
            print("5. Load wallet")
            print("6. Save keys")
            print("h. hack blockchain")
            print("q: quit")

            user_choice = self.get_user_choice()
            if user_choice == '1':
                recipient, amount = self.get_transaction_values()
                signature = self.wallet.sign_transaction(self.wallet.public_key, recipient, amount)
                if self.blockchain.add_transaction(recipient, self.wallet.public_key, signature, amount=float(amount)):
                    print("Transaction added")
                else:
                    print("Transaction error")

            elif user_choice == '2':
                if not self.blockchain.mine_block():
                    print('Mining went wrong, you have a wallet?')
            elif user_choice == '3':
                self.print_blockchain_elements()
            elif user_choice == '4':
                self.wallet.create_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif user_choice == '5':
                self.wallet.load_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif user_choice == '6':
                self.wallet.save_keys()
            elif user_choice == 'q':
                waiting_for_input = False
            if not Verification.verify_chain(self.blockchain.chain):
                self.print_blockchain_elements()
                waiting_for_input = False
            print('Balance of {}: {:.2f}'.format(self.wallet.public_key[:10], self.blockchain.get_balance()))
        else:
            print("User left")


if __name__ == '__main__':
    node = Node()
    node.listen_for_input()
