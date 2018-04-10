#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
import hashlib
from argparse import ArgumentParser
from urllib.parse import urlparse

from flask import Flask, jsonify, request
import requests

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

        # nodes in the peer to peer network
        self.nodes = set()

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
            'sender'   : sender,
            'recipient': recipient,
            'amount'   : amount,
        }

        self.current_transactions.append(transaction)
        return blockchain.blocks[-1].index + 1

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)


def is_valid(chain):
    """
    Check if a given blockchain(the chain itself) is valid or not.

    :param chain: Response from url http://{}/full_chain
    :return:
    """
    if not chain:
        return False

    blocks = chain['blocks']
    length = chain['length']

    # if len(blockchain.blocks) != length:
    #     return False

    if len(blocks) != length:
        return False

    last_block = Block(blocks[0]['index'], blocks[0]['timestamp'], blocks[0]['transactions'], blocks[0]['proof'],
                       blocks[0]['previous_hash'])
    index = 1

    while index < length:
        block = Block(blocks[index]['index'], blocks[index]['timestamp'], blocks[index]['transactions'],
                      blocks[index]['proof'], blocks[index]['previous_hash'])
        if block.previous_hash != last_block.block_hash():
            return False
        if not validate_proof(block.proof, last_block.proof, block.previous_hash):
            return False
        index += 1
        last_block = block

    return True


def consensus():
    """
    Replace local chain with the longest chain in all nodes.

    :return: True if local blockchain is updated
    """
    max_length = len(blockchain.blocks)
    update_blocks = None

    for node in blockchain.nodes:
        r = requests.get(f'http://{node}/full_chain')
        if r.status_code == 200:
            length = r.json()['length']
            blocks = r.json()['blocks']

            if length > max_length and is_valid(r.json()):
                max_length = length
                update_blocks = blocks

    if update_blocks:
        new_chain = []
        for block in update_blocks:
            new_chain.append(
                Block(block['index'], block['timestamp'], block['transactions'], block['proof'],
                      block['previous_hash'], ))
        blockchain.blocks = new_chain
        return True

    return False


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


@app.route('/full_chain', methods=['GET'])
def full_chain():
    """
    Get all blocks in the chain.

    :return:
    """
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
    """
    Create a new block and add it to the chain.

    :return:
    """
    previous_block = blockchain.blocks[-1]
    previous_hash = previous_block.block_hash()
    index = len(blockchain.blocks)
    timestamp = time.time()
    transactions = blockchain.current_transactions
    proof = proof_of_work(blockchain)
    block = Block(index, timestamp, transactions, proof, previous_hash)
    blockchain.add_block(block)
    return jsonify(block.__dict__), 200

#
# @app.route('/isValid', methods=['GET'])
# def isValid():
#     r = requests.get('http://localhost:5001/full_chain')
#     print(r.json())
#     result = is_valid(r.json())
#     return jsonify(f'{result}'), 200


@app.route('/register_nodes', methods=['POST'])
def register_nodes():
    """
    Add nodes to the network

    :return:
    """
    values = request.get_json()
    nodes = values['nodes']

    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message'  : "nodes have been added.",
        'all nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/resolve', methods=['GET'])
def resolve():
    result = consensus()
    blocks_list = []
    for block in blockchain.blocks:
        blocks_list.append(block.__dict__)
    if result:

        response = {
            'message'  : "Chain is updated",
            'new chain': blocks_list,
        }
    else:
        response = {
            'message': "Local chain is active.",
            'chain'  : blocks_list,
        }

    return jsonify(response), 200


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int,  help='port to listen on.')

    args = parser.parse_args()
    port = args.port

    app.run(host='localhost', port=port)
