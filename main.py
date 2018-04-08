#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
import hashlib

from flask import Flask, jsonify, request

app = Flask(__name__)


class Block:
    def __init__(self, index, timestamp, transactions, proof, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.proof = proof

    def block_hash(self):
        """
        create sha256 hash of the block

        :return:
        """
        block_content = json.dumps(self, default=lambda obj: obj.__dict__).encode()
        print(block_content)
        return hashlib.sha256(block_content).hexdigest()


class Blockchain:
    def __init__(self):
        self.blocks = []
        self.current_transactions = []

        # add genesis block when init
        genesis_block = Block(0, time.time(), None, 0, '0')
        self.add_block(genesis_block)

    def add_block(self, block):
        """
        Add a new block to the chain, meanwhile reset the current transaction list.


        :param block:
        """
        self.blocks.append(block)
        self.current_transactions = []

    def new_transaction(self, sender, recipient, amount):
        """
        Create a new transaction, which will be stored in the next mined block.

        :param sender:
        :param recipient:
        :param amount:

        :return: the index of the block which the transaction will be.
        """
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        }

        self.current_transactions.append(transaction)
        return blockchain.blocks[-1].index + 1


def proof_of_work(blockchain):
    """
    simple PoW algorithm.
    Find proof such that hash(proof + previous_proof + previous_hash) starts with 4 zeros.

    :param blockchain:
    :return: <int> new proof
    """
    previous_block = blockchain.blocks[-1]
    previous_hash = previous_block.block_hash()
    previous_proof = previous_block.proof

    proof = 0

    while not validate_proof(proof, previous_proof, previous_hash):
        proof += 1

    return proof


def validate_proof(proof, previous_proof, previous_hash):
    """
    Check if proof is valid.

    :param proof: <int>
    :param previous_proof: <int>
    :param previous_hash: <str>
    :return: <bool> True if proof is valid, false if not.
    """
    guess = f'{proof}{previous_proof}{previous_hash}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:4] == "0000"


def pow_time_test():
    start = time.time()
    proof = 0
    while not validate_proof(proof, 0, 0):
        proof += 1

    end = time.time()
    print(f'Time spent: {end-start}s')
    return proof


blockchain = Blockchain()


@app.route('/blocks', methods=['GET'])
def blocks():
    blocks_list = []
    for block in blockchain.blocks:
        blocks_list.append(block.__dict__)
    response = {
        'blocks': blocks_list,
        'length': len(blockchain.blocks),
    }
    return jsonify(response), 200


@app.route('/transact', methods=['POST'])
def transact():
    print(request.get_data())
    print(request.get_json())
    values = request.get_json()
    print(values)
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Bad request.', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    return jsonify(f'The transaction will be stored in block{index}'), 200


@app.route('/mine', methods=['GET'])
def mine():
    previous_block = blockchain.blocks[-1]
    previous_hash = previous_block.block_hash()
    index = len(blockchain.blocks)
    timestamp = time.time()
    transactions = blockchain.current_transactions
    proof = proof_of_work(blockchain)
    block = Block(index, timestamp, transactions, proof, previous_hash)
    blockchain.add_block(block)
    return jsonify(block.__dict__), 200


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
