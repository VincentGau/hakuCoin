#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from main import Block, Blockchain
import wallet


class BlockchainTestCase(TestCase):
    def setUp(self):
        self.blockchain = Blockchain()

    def test_register_node(self):
        self.blockchain.register_node('http://localhost:8000')

        self.assertIn('localhost:8000', self.blockchain.nodes)

    def test_init_blocks(self):
        self.assertEqual(self.blockchain.blocks.__len__(), 1)
        self.assertEqual(self.blockchain.current_transactions.__len__(), 0)


    def test_new_transaction(self):
        self.blockchain.new_transaction(
            sender='A',
            recipient='B',
            amount=10,
        )
        self.assertEqual(self.blockchain.current_transactions.__len__(), 1)
