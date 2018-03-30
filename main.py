#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle
import time
import hashlib


class Block:
    def __init__(self, index, timestamp, transactions, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash

    def block_hash(self):
        """
        create sha256 hash of the block

        :return:
        """
        block_content = pickle.dumps(self)
        return hashlib.sha256(block_content).hexdigest()



def proof_of_work():
    pass

blockchain = []
genesis_block = Block(0, time.time(), None, '0')
blockchain.append(genesis_block)
