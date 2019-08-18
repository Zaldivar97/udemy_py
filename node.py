from flask import Flask, jsonify, request
from flask_cors import CORS

from wallet import Wallet
from blockchain import Blockchain
from block import Block

app = Flask(__name__)
wallet = Wallet()
blockchain = Blockchain(wallet.public_key)
CORS(app)


@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()
    if wallet.save_keys():
        response = util()
        return jsonify(response), 201
    else:
        response = {
            'message': 'Saving the keys failed'
        }
        return jsonify(response), 500


@app.route('/wallet', methods=['GET'])
def load_keys():
    if wallet.load_keys():
        response = util()
        return jsonify(response), 200
    else:
        response = {
            'message': 'Loading the keys failed'
        }
        return jsonify(response), 500


@app.route('/', methods=['GET'])
def get_ui():
    return 'works'


@app.route('/chain', methods=['GET'])
def get_chain():
    chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash,
                                                [tx.__dict__ for tx in block_el.transactions],
                                                block_el.proof, block_el.time) for block_el
                                          in blockchain.chain]]
    response = {
        'message': 'fetched chain successfully',
        'blockchain': chain
    }
    return jsonify(response), 200


@app.route('/balance', methods=['GET'])
def balance():
    balance = blockchain.get_balance()
    if balance is not None:
        response = {
            'message': 'Fetched balance successfully',
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Loading balance failed',
            'wallet_set_up': wallet.public_key is not None
        }
        return jsonify(response), 500


@app.route('/transactions', methods=['GET'])
def get_open_transactions():
    transactions = blockchain.get_open_transactions()
    if transactions:
        converted_trasactions = [tx.__dict__ for tx in transactions]
        response = {
            'message': 'fetched transactions successfully',
            'transactions': converted_trasactions
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'There\'s no open transactions'
        }
        return jsonify(response), 500


@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet.public_key is None:
        response = {
            'message': 'The wallet is not created'
        }
        return jsonify(response), 400
    values = request.get_json()
    if not values:
        response = {
            'message': 'no data found'
        }
        return jsonify(response), 400
    required_fields = ['recipient', 'amount']
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Required data is missing'
        }
        return jsonify(response), 400
    recipient = values['recipient']
    amount = values['amount']
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)
    if blockchain.add_transaction(recipient, wallet.public_key, signature, amount):
        response = {
            'message': 'Transaction added successfully',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': recipient,
                'amount': amount,
                'signature': signature
            },
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'creating a transaction failed'
        }
        return jsonify(response), 500


@app.route('/mine', methods=['POST'])
def mine():
    block = blockchain.mine_block()
    if block is not None:
        copied_block = block.__dict__.copy()
        copied_block['transactions'] = [tx.__dict__ for tx in copied_block['transactions']]
        response = {
            'message': 'Block added successfully',
            'block': copied_block,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Adding a block failed',
            'wallet_set_up': wallet.public_key is not None
        }
        return jsonify(response), 500


def util():
    global blockchain
    blockchain.hosting = wallet.public_key
    response = {
        'public_key': wallet.public_key,
        'private_key': wallet.private_key,
        'funds': blockchain.get_balance()
    }
    return response


if __name__ == '__main__':
    app.run(host='localhost', port=8080)
