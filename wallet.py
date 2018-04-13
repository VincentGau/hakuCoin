#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import hashlib
import ecdsa
import time

import requests


def generate_keys_file():
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

    filename = f'{time.strftime("%Y%m%d%H%M%S", time.localtime())}.txt'
    print(filename)
    with open(filename, 'w') as f:
        f.write(
            f'private key: {private_key.decode()}\n'
            f'public_key: {public_key.decode()}\n'
            f'wallet address: {address.decode()}'
        )

    return private_key.decode(), public_key.decode(), address.decode()


# generate_keys_file()


def transaction_digest(sender, recipient, amount):
    """
    generate digest for transaction data. Tamper-proofing.

    :param sender:
    :param recipient:
    :param amount:
    :return: <str>
    """
    str_msg = f'{sender}{recipient}{str(amount)}'
    digest = hashlib.sha256(str_msg.encode()).hexdigest()
    return digest


def sign_the_msg(private_key, msg):
    """
    sign the transaction message with the private key.

    :param private_key: <base64>
    :param msg: <str> digest of transaction data.
    :return: <base64> signature
    """
    message = hashlib.sha256(msg.encode()).hexdigest().encode()
    private_key = base64.b64decode(private_key)

    sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)

    signature = sk.sign(message)
    signature = base64.b64encode(signature)

    return signature.decode()


def new_transaction(sender, recipient, amount, private_key, public_key):
    """
    claim a transaction.

    :param sender:
    :param recipient:
    :param amount:
    :param private_key:
    :param public_key:
    """
    digest = transaction_digest(sender, recipient, amount)
    signature = sign_the_msg(private_key, digest)
    payload = {
        'sender'    : sender,
        'recipient' : recipient,
        'amount'    : amount,
        'signature' : signature,
        'public_key': public_key,
        'message'   : digest,
    }
    transaction_url = 'http://localhost:5000/transact_safe'
    r = requests.post(transaction_url, json=payload)
    print(r.text)


new_transaction('8A8SBdlpocLp7FyN/GtyHZrEXWywjKF/79XTy/VV9w8=', 'X5fQABW6aPix8owEIYAYUjZrsp8T16VrEY1JE316kgM=', 10,
                '4VgkCrHM6upSIukzSYSwzcKgvUKUZbPDfeGRp80R6X4=',
                'p9Gm6kGjC/nWr+lGTDy3HCQXCaBZRJst4dG7rFdTWGoo39Wiw6tlZ8tvSF2YUivFfxDCOZsihAujUhr7XgPDYg==')
