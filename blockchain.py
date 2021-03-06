#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A simple blockchain.
"""

import base64
import time
import hashlib
from argparse import ArgumentParser
from urllib.parse import urlparse

import ecdsa
from flask import Flask, jsonify, request
import requests

import local_config

app = Flask(__name__)


class Block:
    """
    Actually no need to create a class for block. Could simply use a dict to represent block.
    """
    def __init__(self, index, timestamp, transactions, proof, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.proof = proof
        self.hash = self.block_hash()

    def block_hash(self):
        """
        create sha256 hash of the block

        :return:
        """
        sha = hashlib.sha256()
        sha.update((str(self.index) + str(self.timestamp) + str(self.transactions) + str(self.previous_hash) + str(
            self.proof)).encode())
        return sha.hexdigest()


class Blockchain:
    def __init__(self):
        self.blocks = []
        self.current_transactions = []

        # nodes in the peer to peer network
        self.nodes = local_config.NODES

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

    def transaction_safe(self, sender, recipient, amount, public_key, signature, msg):
        """
        Create a new transaction, which will be stored in the next mined block.
        Tamper-proofing & identity verified.

        :param sender:
        :param recipient:
        :param amount:
        :param public_key:
        :param signature:
        :param msg:
        :return:
        """
        if validate_signature(public_key, signature, msg):
            current_transaction = {
                'sender'   : sender,
                'recipient': recipient,
                'amount'   : amount,
            }
            self.current_transactions.append(current_transaction)
            return blockchain.blocks[-1].index + 1

    def register_node(self, address):
        """
        register address to the network nodes set()
        :param address:
        """
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


def proof_of_work(bc):
    """
    simple PoW algorithm.
    Find proof such that hash(proof + previous_proof + previous_hash) starts with 4 zeros.

    :param bc: blockchain
    :return: <int> new proof
    """
    previous_block = bc.blocks[-1]
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
    """
    Time elapsed of different difficulty.

    :return:
    """
    start = time.time()
    proof = 0
    while not validate_proof(proof, 0, 0):
        proof += 1

    end = time.time()
    print(f'Time spent: {end-start}s')
    return proof


def generate_keys():
    """
    Generate private key, public key, and address.

    :return: <str>
    """
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()

    # <str>
    private_key = sk.to_string().hex()
    public_key = vk.to_string().hex()
    address = hashlib.sha256(private_key.encode()).hexdigest()

    # <bytes>
    private_key = base64.b64encode(bytes.fromhex(private_key))
    public_key = base64.b64encode(bytes.fromhex(public_key))
    address = base64.b64encode(bytes.fromhex(address))

    return private_key.decode(), public_key.decode(), address.decode()


def validate_signature(public_key, signature, msg):
    """
    validate signature. verify identity and tamper resistant.

    :param public_key: <base64>
    :param signature: <base64>
    :param msg:
    :return:
    """

    public_key = base64.b64decode(public_key)

    vk = ecdsa.VerifyingKey.from_string(public_key, curve=ecdsa.SECP256k1)
    signature = base64.b64decode(signature)

    try:
        hash_msg = hashlib.sha256(msg.encode()).hexdigest()
        vk.verify(signature, hash_msg.encode())
        print("PASS")
    except Exception:
        print("REJECTED")
        return False

    return True


# init
blockchain = Blockchain()
priv, pub, addr = generate_keys()


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


@app.route('/nodes', methods=['GET'])
def nodes():
    """
    Show all nodes.

    :return:
    """
    response = {
        'nodes' : list(blockchain.nodes),
        'length': len(blockchain.nodes),
    }
    return jsonify(response), 200


@app.route('/transact', methods=['POST'])
def transact():
    """
    Claim a new transaction

    :return:
    """
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Bad request.', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    return jsonify(f'The transaction will be stored in block{index}'), 200


@app.route('/transact_safe', methods=['POST'])
def transact_safe():
    """
    Claim a new transaction. With signature.

    :return:
    """
    values = request.get_json()
    required = ['sender', 'recipient', 'amount', 'signature', 'message']
    if not all(k in values for k in required):
        return 'Bad request.', 400

    index = blockchain.transaction_safe(values['sender'], values['recipient'], values['amount'], values['public_key'],
                                        values['signature'], values['message'])
    return jsonify(f'The transaction will be stored in block{index}'), 200


@app.route('/mine', methods=['GET'])
def mine():
    """
    Create a new block and add it to the chain.

    :return:
    """

    # reward for finding the proof, in this case sender is 0.
    blockchain.new_transaction(sender=0, recipient=addr, amount=1)

    previous_block = blockchain.blocks[-1]
    previous_hash = previous_block.block_hash()
    index = len(blockchain.blocks)
    timestamp = time.time()
    transactions = blockchain.current_transactions
    proof = proof_of_work(blockchain)
    block = Block(index, timestamp, transactions, proof, previous_hash)
    blockchain.add_block(block)

    return jsonify(block.__dict__), 200


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
    """
    Resolve conflict. Update current blockchain with the longest one in the network.

    :return:
    """
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


@app.route('/wallet', methods=['GET'])
def wallet():
    """
    Apply for a new wallet.

    :return:
    """

    private_key, public_key, address = generate_keys()

    response = {
        'address'    : address,
        'private_key': private_key,
        'public_key' : public_key,
    }
    return jsonify(response), 200


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on.')

    args = parser.parse_args()
    port = args.port

    app.run(host='localhost', port=port)
