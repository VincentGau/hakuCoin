#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time


class Block:
    def __init__(self, index, timestamp, transactions, previoid_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previoid_hash = previoid_hash

    def get_hash(self):
        """
        get hash of the block

        :return:
        """


blockchain = []
genesis_block = Block(0, time.time(), None, '0')
blockchain.append(genesis_block)