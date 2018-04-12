#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import hashlib
import ecdsa


def generate_keys():
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()

    print(f'{sk.to_string().hex()}\n{vk.to_string()}')


def sign_the_msg(private_key, msg):
    """
    sign the message with the private key.

    :param private_key: <base64>
    :param msg: <str>
    :return: <base64> signature
    """
    message = hashlib.sha256(msg.encode()).hexdigest().encode()
    private_key = base64.b64decode(private_key)

    sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)

    signature = sk.sign(message)
    signature = base64.b64encode(signature)

    return signature


def validate_signature(public_key, signature, msg):
    print(public_key)
    public_key = base64.b64decode(public_key)

    vk = ecdsa.VerifyingKey.from_string(public_key, curve=ecdsa.SECP256k1)
    print(base64.b64encode(bytes.fromhex(vk.to_string().hex())).decode())
    signature = base64.b64decode(signature)
    # print(signature)
    try:
        vk.verify(signature, hashlib.sha256(msg.encode()).hexdigest().encode())
        print("PASS")
    except Exception:
        print("REJECTED")
        return False

    return True


prik = 'BiAjFNixl0WB+APngu8Uh5psx9f/HHhFwWbBn0d+CmQ='
pubk = 'Qj4TRlymO0Me73IXfoU+5MqJq7sFEJcuEtJlZldPDp4slzQWPMs13YMemF3RhJQ8MuVPjToIXdbpjZngOoI4ow=='

sig = sign_the_msg(prik, 'haku')
validate_signature(pubk, sig, 'haku')
