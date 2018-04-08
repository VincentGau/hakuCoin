#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
import hashlib


class Block:
    def __init__(self, index, timestamp, transactions, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.hash = self.block_hash()

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


def proof_of_work(blockchain):
    """
    simple PoW algorithm.
    Find proof such that hash(proof + previous_proof + previous_hash) starts with 4 zeros.

    :param blockchain:
    :return: <int> new proof
    """
    previous_block = blockchain[-1]
    previous_hash = previous_block.block_hash()
    previous_proof = previous_block['proof']

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


def test_pow_time():
    start = time.time()
    proof = 0
    while not validate_proof(proof, 0, 0):
        proof += 1

    end = time.time()
    print(f'Time spent: {end-start}s')
    return proof


blockchain = []
genesis_block = Block(0, time.time(), None, '0')
blockchain.append(genesis_block)

print(test_pow_time())
