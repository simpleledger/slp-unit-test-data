#!/usr/bin/env python3
"""
Generates the tx_input_tests.json file.
"""

# This script needs to call library functions from an SLP-enabled version of
# electron cash. Modify the directory name to point to your local copy of the
# electron cash repository (which should contain a subdirectory 'lib/').
import sys
sys.path.append('../electron_cash/')
sys.path.append('../electron-cash/')
sys.path.append('../electroncash/')

from lib.address import (PublicKey, Address, Script, ScriptOutput, hash160,
                      UnknownAddress, OpCodes as opcodes)

from lib.transaction import Transaction

from lib.networks import NetworkConstants

from lib.bitcoin import TYPE_SCRIPT, TYPE_ADDRESS

from lib import slp

import json


# Alice = address hash 'aaaa...'  (qz4242424242424242424242424242424gnum7slus)
alice  = Address.from_P2PKH_hash(bytes.fromhex('aa'*20))

# Bob   = address hash 'b0b0...'  (qzctpv9skzctpv9skzctpv9skzctpv9skq64j03a5v)
bob    = Address.from_P2PKH_hash(bytes.fromhex('b0'*20))

# Carol = address hash 'cccc...'  (qrxvenxvenxvenxvenxvenxvenxvenxveswaaztglj)
carol  = Address.from_P2PKH_hash(bytes.fromhex('cc'*20))

# Dave  = address hash 'dada...'  (qrdd4kk6mtdd4kk6mtdd4kk6mtdd4kk6mgupqafea9)
dave   = Address.from_P2PKH_hash(bytes.fromhex('da'*20))

# Eve   = address hash 'eeee...'  (qrhwamhwamhwamhwamhwamhwamhwamhwacyxleslj2)
eve    = Address.from_P2PKH_hash(bytes.fromhex('ee'*20))

# Frank = address hash 'ffff...'  (qrlllllllllllllllllllllllllllllllu5y7pl6pz)
frank  = Address.from_P2PKH_hash(bytes.fromhex('ff'*20))

print(alice, bob, carol, dave, eve, frank)

# Fake token_ids for when a real genesis is not required
fake_token_id1 = "88"*32
fake_token_id2 = "99"*32



## Check helper builder vs manual builder --
#assert(slp.buildGenesisOpReturnOutput_V1('', '', '', '', 0, None, 100)
       #==
       #slp.chunksToOpreturnOutput([b'SLP\x00', b'\x01', b'GENESIS', b'', b'', b'', b'', b'\x00', b'', (100).to_bytes(8,'big')]))


### Helper functions

def fakeinput(txid, vout):
    """ Create an input record with empty scriptSig, as appropriate for Transaction object. """
    return {'prevout_hash':txid, 'prevout_n':vout, 'sequence':0, 'x_pubkeys': [], 'pubkeys': [], 'address': None, 'type': 'unknown', 'signatures': [], 'num_sig': 0, 'scriptSig': ''}


alltxes = dict() # txid -> raw
def maketx(inputs, outputs):
    """
    Make a transaction from the given inputs and outputs list. Saves the serialized tx to `alltxes` and returns the key (its txid).
    """
    tx = Transaction.from_io(inputs, outputs)
    txid = tx.txid()
    raw = str(tx)     # ensure we work with serialized version.
    #txid = Transaction(raw).txid() # re-deserialize to make sure we get the right txid

    alltxes[txid] = raw

    print("Generated %.10s... (%d -> %d)"%(txid, len(inputs), len(outputs)))

    return txid


### TESTS


tests = []


## DAG 1 - basic GENESIS then various variants of SEND / MINT

# txid to represent a source of 'BCH change'
btxid = maketx([], [(TYPE_ADDRESS, eve, 10**8), (TYPE_ADDRESS, eve, 10**8), (TYPE_ADDRESS, eve, 10**8), (TYPE_ADDRESS, eve, 10**8),])

txid1 = maketx([  # GENESIS
                 fakeinput(btxid,0),
                ],
               [
                 slp.buildGenesisOpReturnOutput_V1('', '', '', '', 0, 2, 100),
                 (TYPE_ADDRESS, alice, 5),
                 (TYPE_ADDRESS, bob, 5),
                 (TYPE_ADDRESS, frank, 100),
                ])
txid2 = maketx([  # SEND from the send output
                 fakeinput(btxid,1),
                 fakeinput(txid1,1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(txid1, [50,50]),
                 (TYPE_ADDRESS, bob, 5),
                 (TYPE_ADDRESS, carol, 5),
                ])
txid3 = maketx([  # SEND that uses both token and baton
                 fakeinput(btxid,1),
                 fakeinput(txid1,1),
                 fakeinput(txid1,2),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(txid1, [50,50]),
                 (TYPE_ADDRESS, bob, 5),
                 (TYPE_ADDRESS, carol, 5),
                ])
txid4 = maketx([  # SEND that uses only the baton
                 fakeinput(btxid,1),
                 fakeinput(txid1,2),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(txid1, [50,50]),
                 (TYPE_ADDRESS, bob, 5),
                 (TYPE_ADDRESS, carol, 5),
                ])
txid5 = maketx([  # MINT that uses only the baton
                 fakeinput(btxid,1),
                 fakeinput(txid1,2),
                ],
               [
                 slp.buildMintOpReturnOutput_V1(txid1, None, 23),
                 (TYPE_ADDRESS, bob, 5),
                 (TYPE_ADDRESS, carol, 5),
                ])
txid6 = maketx([  # MINT that uses both baton and tokens
                 fakeinput(txid1,1),
                 fakeinput(btxid,1),
                 fakeinput(txid1,2),
                ],
               [
                 slp.buildMintOpReturnOutput_V1(txid1, None, 23),
                 (TYPE_ADDRESS, bob, 5),
                 (TYPE_ADDRESS, carol, 5),
                ])
txid7 = maketx([  # MINT that uses just tokens
                 fakeinput(txid1,1),
                 fakeinput(btxid,1),
                ],
               [
                 slp.buildMintOpReturnOutput_V1(txid1, None, 23),
                 (TYPE_ADDRESS, bob, 5),
                 (TYPE_ADDRESS, carol, 5),
                ])

tests.extend([
    dict(description = "When the input is an SLP-invalid BCH-only tx, the GENESIS tx should be SLP-valid.",
         when   = [ dict(tx = alltxes[btxid], valid=False) ],
         should = [ dict(tx = alltxes[txid1], valid=True), ],
         ),
    dict(description = "When the inputs are an SLP-invalid BCH-only tx and an SLP-valid GENESIS tx (spending its token output), the SEND tx should be SLP-valid.",
         when   = [ dict(tx = alltxes[btxid], valid=False), dict(tx = alltxes[txid1], valid=True) ],
         should = [ dict(tx = alltxes[txid2], valid=True) ],
         ),
    dict(description = "When the inputs are an SLP-invalid BCH-only tx and an SLP-valid GENESIS tx (spending both its token AND baton output), the SEND tx should be SLP-valid.",
         when   = [ dict(tx = alltxes[btxid], valid=False), dict(tx = alltxes[txid1], valid=True) ],
         should = [ dict(tx = alltxes[txid3], valid=True) ],
         ),
    dict(description = "When the inputs are an SLP-invalid BCH-only tx and an SLP-valid GENESIS tx (spending only its baton output), the SEND tx should be SLP-invalid.",
         when   = [ dict(tx = alltxes[btxid], valid=False), dict(tx = alltxes[txid1], valid=True) ],
         should = [ dict(tx = alltxes[txid4], valid=False) ],
         ),
    dict(description = "When the inputs are an SLP-invalid BCH-only tx and an SLP-valid GENESIS tx (spending only its baton output), the MINT tx should be SLP-valid.",
         when   = [ dict(tx = alltxes[btxid], valid=False), dict(tx = alltxes[txid1], valid=True) ],
         should = [ dict(tx = alltxes[txid5], valid=True) ],
         ),
    dict(description = "When the inputs are an SLP-invalid BCH-only tx and an SLP-valid GENESIS tx (spending both its token AND baton output), the MINT tx should be SLP-valid.",
         when   = [ dict(tx = alltxes[btxid], valid=False), dict(tx = alltxes[txid1], valid=True) ],
         should = [ dict(tx = alltxes[txid6], valid=True) ],
         ),
    dict(description = "When the inputs are an SLP-invalid BCH-only tx and an SLP-valid GENESIS tx (spending its token output), the MINT tx should be SLP-invalid.",
         when   = [ dict(tx = alltxes[btxid], valid=False), dict(tx = alltxes[txid1], valid=True) ],
         should = [ dict(tx = alltxes[txid7], valid=False) ],
         ),
    ])


## DAG 2 - large input sum and output sum >= 2**64

txid1 = maketx([
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id2, [2**64-100]),
                 (TYPE_ADDRESS, alice, 546),
                ])
txid2 = maketx([
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id2, [1000000]),
                 (TYPE_ADDRESS, alice, 547),
                ])
txid3 = maketx([
                fakeinput(txid1, 1),
                fakeinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id2, [2**64 - 1000000, 1999900]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid4 = maketx([
                fakeinput(txid1, 1),
                fakeinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id2, [2**64 - 1000000, 1999901]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid5 = maketx([
                fakeinput(txid1, 1),
                fakeinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id2, [2**64 - 1000000, 1999899]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid6 = maketx([
                fakeinput(txid1, 1),
                fakeinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id2, [100, 100]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid7 = maketx([
                fakeinput(txid1, 1),
                fakeinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id2, [0, 0, 0, 2**64-1, 2**64-1]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])

tests.extend([
    dict(description = "When the token input amounts are (2**64-100, 1000000) and the SEND outputs exactly this amount, the SEND tx should be valid (output summation must not use 64-bit integers that overflow).",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=True), ],
         should = [ dict(tx = alltxes[txid3], valid=True), ],
         ),
    dict(description = "When the token input amounts are (2**64-100, 1000000) and the SEND outputs exceed this by 1 token, the SEND tx should be invalid.",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=True), ],
         should = [ dict(tx = alltxes[txid4], valid=False), ],
         ),
    dict(description = "When the token input amounts are (2**64-100, 1000000) and the SEND outputs fall short by 1 token, the SEND tx should be valid.",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=True), ],
         should = [ dict(tx = alltxes[txid5], valid=True), ],
         ),
    dict(description = "When the token input amounts are (2**64-100, 1000000) and the SEND outputs are very small numbers, the SEND tx should be valid.",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=True), ],
         should = [ dict(tx = alltxes[txid6], valid=True), ],
         ),
    dict(description = "When the token input amounts are (2**64-100, 1000000) but the sum of SEND outputs exceeds this (even when the token outputs will be truncated), the SEND tx should be invalid.",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=True), ],
         should = [ dict(tx = alltxes[txid7], valid=False), ],
         ),
    ])

with open('tx_input_tests.json', 'w') as f:
    json.dump(tests, f, indent=1)
