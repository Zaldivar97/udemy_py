from uuid import uuid4

from verification import Verification
from blockchain import Blockchain


class Node:
    def __init__(self):
        # self.id = str(uuid4())
        self.id = 'Steven'
        self.blockchain = Blockchain(self.id)

    def get_transaction_values(self):
        recipient = input("Recipient:")
        amount = input("Amount:")
        return recipient, amount

    def get_user_choice(self):
        choice = input('Enter an option: ')
        return choice

    def print_blockchain_elements(self):
        if len(self.blockchain.get_chain()) > 0:
            for block in self.blockchain.get_chain():
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
            print("h. hack blockchain")
            print("q: quit")

            user_choice = self.get_user_choice()
            if user_choice == '1':
                recipient, amount = self.get_transaction_values()
                if self.blockchain.add_transaction(recipient, self.id, amount=float(amount)):
                    print("Transaction added")
                else:
                    print("Transaction error")
            elif user_choice == '2':
                self.blockchain.mine_block()
            elif user_choice == '3':
                self.print_blockchain_elements()
            elif user_choice == 'q':
                waiting_for_input = False
            if not Verification.verify_chain(self.blockchain.get_chain()):
                self.print_blockchain_elements()
                waiting_for_input = False
            print('Balance of {}: {:.2f}'.format(self.id, self.blockchain.get_balance()))
        else:
            print("User left")


node = Node()
node.listen_for_input()
