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

def mkinput(txid, vout):
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
                 mkinput(btxid,0),
                ],
               [
                 slp.buildGenesisOpReturnOutput_V1('', '', '', '', 0, 2, 100),
                 (TYPE_ADDRESS, alice, 5),
                 (TYPE_ADDRESS, bob, 5),
                 (TYPE_ADDRESS, frank, 100),
                ])
genesis_txid = txid1
txid2 = maketx([  # SEND from the send output
                 mkinput(btxid,1),
                 mkinput(txid1,1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(txid1, [50,50]),
                 (TYPE_ADDRESS, bob, 5),
                 (TYPE_ADDRESS, carol, 5),
                ])
txid3 = maketx([  # SEND that uses both token and baton
                 mkinput(btxid,1),
                 mkinput(txid1,1),
                 mkinput(txid1,2),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(txid1, [50,50]),
                 (TYPE_ADDRESS, bob, 5),
                 (TYPE_ADDRESS, carol, 5),
                ])
txid4 = maketx([  # SEND that uses only the baton
                 mkinput(btxid,1),
                 mkinput(txid1,2),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(txid1, [50,50]),
                 (TYPE_ADDRESS, bob, 5),
                 (TYPE_ADDRESS, carol, 5),
                ])
txid5 = maketx([  # MINT that uses only the baton
                 mkinput(btxid,1),
                 mkinput(txid1,2),
                ],
               [
                 slp.buildMintOpReturnOutput_V1(txid1, None, 23),
                 (TYPE_ADDRESS, bob, 5),
                 (TYPE_ADDRESS, carol, 5),
                ])
txid5a = maketx([  # MINT that uses only the baton
                 mkinput(btxid,1),
                 mkinput(txid1,2),
                ],
               [
                 slp.buildMintOpReturnOutput_V2(txid1, None, 23),
                 (TYPE_ADDRESS, bob, 5),
                 (TYPE_ADDRESS, carol, 5),
                ])
txid6 = maketx([  # MINT that uses both baton and tokens
                 mkinput(txid1,1),
                 mkinput(btxid,1),
                 mkinput(txid1,2),
                ],
               [
                 slp.buildMintOpReturnOutput_V1(txid1, None, 23),
                 (TYPE_ADDRESS, bob, 5),
                 (TYPE_ADDRESS, carol, 5),
                ])
txid7 = maketx([  # MINT that uses just tokens
                 mkinput(txid1,1),
                 mkinput(btxid,1),
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
     dict(description = "When the inputs are an SLP-invalid BCH-only tx and an SLP-valid GENESIS tx (spending only its baton output), the MINT tx should be SLP-invalid since version/type changed.",
         when   = [ dict(tx = alltxes[btxid], valid=False), dict(tx = alltxes[txid1]) ],
         should = [ dict(tx = alltxes[txid5a], valid=False) ],
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
                mkinput(txid1, 1),
                mkinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id2, [2**64 - 1000000, 1999900]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid4 = maketx([
                mkinput(txid1, 1),
                mkinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id2, [2**64 - 1000000, 1999901]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid5 = maketx([
                mkinput(txid1, 1),
                mkinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id2, [2**64 - 1000000, 1999899]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid6 = maketx([
                mkinput(txid1, 1),
                mkinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id2, [100, 100]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid7 = maketx([
                mkinput(txid1, 1),
                mkinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id2, [0, 0, 0, 2**64-1, 2**64-1]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])

tests.extend([
    dict(description = "When the token input amounts are (2**64-100, 1000000) and the SEND outputs exactly this amount, the SEND tx should be SLP-valid (output summation must not use 64-bit integers that overflow).",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=True), ],
         should = [ dict(tx = alltxes[txid3], valid=True), ],
         ),
    dict(description = "When the token input amounts are (2**64-100, 1000000) and the SEND outputs exceed this by 1 token, the SEND tx should be SLP-invalid.",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=True), ],
         should = [ dict(tx = alltxes[txid4], valid=False), ],
         ),
    dict(description = "When the token input amounts are (2**64-100, 1000000) and the SEND outputs fall short by 1 token, the SEND tx should be SLP-valid.",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=True), ],
         should = [ dict(tx = alltxes[txid5], valid=True), ],
         ),
    dict(description = "When the token input amounts are (2**64-100, 1000000) and the SEND outputs are very small numbers, the SEND tx should be SLP-valid.",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=True), ],
         should = [ dict(tx = alltxes[txid6], valid=True), ],
         ),
    dict(description = "When the token input amounts are (2**64-100, 1000000) but the sum of SEND outputs exceeds this (even when the token outputs will be truncated), the SEND tx should be SLP-invalid.",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=True), ],
         should = [ dict(tx = alltxes[txid7], valid=False), ],
         ),
    ])


## DAG 3 - testing incompatible token_ids

txid1 = maketx([
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id1, [1100]),
                 (TYPE_ADDRESS, alice, 546),
                ])
txid2 = maketx([
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id2, [1000]),
                 (TYPE_ADDRESS, alice, 547),
                ])
txid3 = maketx([
                mkinput(txid1, 1),
                mkinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id1, [500, 501]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid4 = maketx([
                mkinput(txid1, 1),
                mkinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id2, [500, 501]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid5 = maketx([
                mkinput(txid1, 1),
                mkinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id2, [0, 0, 500, 501]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])


tests.extend([
    dict(description = "When given two inputs of differing token_id, the SEND should be SLP-valid because it spends less than the matching token_id",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=True), ],
         should = [ dict(tx = alltxes[txid3], valid=True), ],
         ),
    dict(description = "When given two inputs of differing token_id, the SEND should be SLP-invalid because it spends more than the tokens of matching token_id",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=True), ],
         should = [ dict(tx = alltxes[txid4], valid=False), ],
         ),
    dict(description = "When given two inputs of differing token_id, the SEND should be SLP-invalid because it spends more than the tokens of matching token_id",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=True), ],
         should = [ dict(tx = alltxes[txid5], valid=False), ],
         ),
    ])


## DAG 4 - Input summation tests including invalid inputs

txid1 = maketx([
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id1, [300,1000]),
                 (TYPE_ADDRESS, alice, 546),
                 (TYPE_ADDRESS, alice, 546),
                ])
txid2 = maketx([
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id1, [400,1000]),
                 (TYPE_ADDRESS, alice, 547),
                 (TYPE_ADDRESS, alice, 546),
                ])
txid3 = maketx([
                mkinput(txid1, 1),
                mkinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id1, [600, 100]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid3a = maketx([
                mkinput(txid1, 1),
                mkinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V2(fake_token_id1, [600, 100]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid4 = maketx([
                mkinput(txid1, 1),
                mkinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id1, [600, 101]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid5 = maketx([
                mkinput(txid1, 1),
                mkinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id1, [100, 200]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid6 = maketx([
                mkinput(txid1, 1),
                mkinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id1, [100, 201]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid7 = maketx([
                mkinput(txid1, 1),
                mkinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id1, [200, 200]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid8 = maketx([
                mkinput(txid1, 1),
                mkinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id1, [200, 201]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid9 = maketx([
                mkinput(txid1, 1),
                mkinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(genesis_txid, [0,0,0,0]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid9a = maketx([
                mkinput(txid1, 1),
                mkinput(txid2, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V2(genesis_txid, [0,0,0,0]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])

tests.extend([
    dict(description = "When given two SLP-valid inputs, the SEND should be SLP-valid since it outputs as much as the valid inputs",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=True), ],
         should = [ dict(tx = alltxes[txid3], valid=True), ],
         ),
     dict(description = "When given two SLP-valid inputs, the SEND should be SLP-invalid since token version/type changed",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=True), ],
         should = [ dict(tx = alltxes[txid3a], valid=False), ],
         ),
    dict(description = "When given two SLP-valid inputs, the SEND should be SLP-invalid since it outputs more than the valid inputs",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=True), ],
         should = [ dict(tx = alltxes[txid4], valid=False), ],
         ),
    dict(description = "When given one SLP-valid input and another SLP-invalid input, the SEND should be SLP-valid since it outputs as much as the valid input",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=False), ],
         should = [ dict(tx = alltxes[txid5], valid=True), ],
         ),
    dict(description = "When given one SLP-valid input and another SLP-invalid input, the SEND should be SLP-invalid since it outputs more than the valid input",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=False), ],
         should = [ dict(tx = alltxes[txid6], valid=False), ],
         ),
    dict(description = "When given one SLP-valid input and another SLP-invalid input, the SEND should be SLP-valid since it outputs as much as the valid input",
         when   = [ dict(tx = alltxes[txid1], valid=False), dict(tx = alltxes[txid2], valid=True), ],
         should = [ dict(tx = alltxes[txid7], valid=True), ],
         ),
    dict(description = "When given one SLP-valid input and another SLP-invalid input, the SEND should be SLP-invalid since it outputs more than the valid input",
         when   = [ dict(tx = alltxes[txid1], valid=False), dict(tx = alltxes[txid2], valid=True), ],
         should = [ dict(tx = alltxes[txid8], valid=False), ],
         ),
    dict(description = "When given two SLP-invalid inputs, the SEND should be SLP-valid since it outputs 0 tokens",
         when   = [ dict(tx = alltxes[txid1], valid=False), dict(tx = alltxes[txid2], valid=False), dict(tx = alltxes[genesis_txid])],
         should = [ dict(tx = alltxes[txid9], valid=True), ],
         ),
     dict(description = "When given two SLP-invalid inputs, the SEND should be SLP-invalid since GENESIS is invalid",
         when   = [ dict(tx = alltxes[txid1], valid=False), dict(tx = alltxes[txid2], valid=False), dict(tx = alltxes[genesis_txid], valid=False)],
         should = [ dict(tx = alltxes[txid9], valid=False), ],
         ),
     dict(description = "When given two SLP-invalid inputs, the 0 output SEND should be SLP-invalid since the version/type is different from GENESIS",
         when   = [ dict(tx = alltxes[txid1], valid=False), dict(tx = alltxes[txid2], valid=False), dict(tx = alltxes[genesis_txid])],
         should = [ dict(tx = alltxes[txid9a], valid=False), ],
         ),
    ])

## DAG 5 - check OP_RETURN placement / multiple OP_RETURN behaviours

txid1 = maketx([
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id1, [300,1000]),
                 (TYPE_ADDRESS, alice, 546),
                 (TYPE_ADDRESS, alice, 546),
                ])
txid2 = maketx([
                mkinput(txid1, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id1, [200,0,20]),
                 (TYPE_ADDRESS, bob, 547),
                 slp.buildSendOpReturnOutput_V1(fake_token_id1, [400,0,20]),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid3 = maketx([
                mkinput(txid1, 1),
                ],
               [
                 slp.buildSendOpReturnOutput_V1(fake_token_id1, [400,0,20]),
                 (TYPE_ADDRESS, bob, 547),
                 slp.buildSendOpReturnOutput_V1(fake_token_id1, [200,0,20]),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid4 = maketx([
                mkinput(txid1, 1),
                ],
               [
                 (TYPE_ADDRESS, dave, 547),
                 slp.buildSendOpReturnOutput_V1(fake_token_id1, [0,400,0,20]),
                 (TYPE_ADDRESS, bob, 547),
                 slp.buildSendOpReturnOutput_V1(fake_token_id1, [0,200,0,20]),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid5 = maketx([
                mkinput(txid1, 1),
                ],
               [
                 (TYPE_ADDRESS, dave, 547),
                 slp.buildSendOpReturnOutput_V1(fake_token_id1, [0,200,0,20]),
                 (TYPE_ADDRESS, bob, 547),
                 (TYPE_ADDRESS, carol, 547),
                ])
txid6 = maketx([
                mkinput(txid1, 1),
                ],
               [
                ])

tests.extend([
    dict(description = "When given valid tokens, the SEND with multiple OP_RETURNS should be SLP-valid based on the vout=0 OP_RETURN",
         when   = [ dict(tx = alltxes[txid1], valid=True), ],
         should = [ dict(tx = alltxes[txid2], valid=True), ],
         ),
    dict(description = "When given valid tokens, the SEND with multiple OP_RETURNS should be SLP-invalid based on the vout=0 OP_RETURN",
         when   = [ dict(tx = alltxes[txid1], valid=True), ],
         should = [ dict(tx = alltxes[txid3], valid=False), ],
         ),
    dict(description = "When given valid tokens, the SEND with multiple OP_RETURNS should be SLP-invalid since vout=0 is not an OP_RETURN",
         when   = [ dict(tx = alltxes[txid1], valid=True), ],
         should = [ dict(tx = alltxes[txid4], valid=False), ],
         ),
    dict(description = "When given valid tokens, the SEND should be SLP-invalid since vout=0 is not an OP_RETURN",
         when   = [ dict(tx = alltxes[txid1], valid=True), ],
         should = [ dict(tx = alltxes[txid5], valid=False), ],
         ),
    ## Skip this test since it would never relay.
    #dict(description = "When given multiple OP_RETURNS, the SEND should be SLP-invalid since vout=0 is nonexistent (not even an OP_RETURN)",
         #when   = [ dict(tx = alltxes[txid1], valid=True), ],
         #should = [ dict(tx = alltxes[txid6], valid=False), ],
         #),
    ])

## DAG 5 - Tests involving transactions following an over-output.

txid1 = maketx([
                ],
               [
                 slp.buildMintOpReturnOutput_V1(fake_token_id1, None, 100),
                 (TYPE_ADDRESS, alice, 546),
                ])
txid2 = maketx([
                mkinput(txid1, 1),
                ],
               [
                slp.buildSendOpReturnOutput_V1(fake_token_id1, [200, 25]),
                (TYPE_ADDRESS, bob, 1),
                (TYPE_ADDRESS, alice, 1),
                ])
txid3 = maketx([
                mkinput(txid2, 2),
                ],
               [
                slp.buildSendOpReturnOutput_V1(fake_token_id1, [25]),
                (TYPE_ADDRESS, carol, 1),
                ])

tests.extend([
    dict(description = "When taking 100 tokens, the SEND should be SLP-invalid since it outputs 225 tokens.",
         when   = [ dict(tx = alltxes[txid1], valid=True), ],
         should = [ dict(tx = alltxes[txid2], valid=False), ],
         ),
    dict(description = "When taking SLP-invalid tokens, the SEND should be SLP-invalid since it sends >0 tokens.",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=False), ],
         should = [ dict(tx = alltxes[txid3], valid=False), ],
         ),
    ])

## DAG 6 - Tests involving a semi-realistic DAG

txid1 = maketx([
                ],
               [
                 slp.buildMintOpReturnOutput_V1(fake_token_id1, 241, 100),
                 (TYPE_ADDRESS, alice, 546),
                ])
txid2 = maketx([
                mkinput(txid1, 1),
                ],
               [
                slp.buildSendOpReturnOutput_V1(fake_token_id1, [50,50]),
                (TYPE_ADDRESS, bob, 1),
                (TYPE_ADDRESS, alice, 1),
                ])
txid3a = maketx([
                mkinput(txid2, 2), # alice spends
                ],
               [
                slp.buildSendOpReturnOutput_V1(fake_token_id1, [40,]),
                (TYPE_ADDRESS, carol, 1),
                ])
txid3b = maketx([
                mkinput(txid2, 2), # alice spends
                ],
               [
                slp.buildSendOpReturnOutput_V1(fake_token_id1, [60,]),
                (TYPE_ADDRESS, carol, 1),
                ])
txid4 = maketx([
                mkinput(txid2, 1), # bob spends
                ],
               [
                slp.buildSendOpReturnOutput_V1(fake_token_id1, [40,]),
                (TYPE_ADDRESS, carol, 1),
                ])
txid5 = maketx([
                mkinput(txid3a, 1), # carol spends 40
                mkinput(txid4, 1),  # carol spends 40
                ],
               [
                slp.buildSendOpReturnOutput_V1(fake_token_id1, [55,]),
                (TYPE_ADDRESS, dave, 1),
                ])


tests.extend([
    dict(description = "When SEND splits tokens from MINT, should be SLP-valid.",
         when   = [ dict(tx = alltxes[txid1], valid=True), ],
         should = [ dict(tx = alltxes[txid2], valid=True), ],
         ),
    dict(description = "When SEND splits tokens from MINT, a further SEND should be SLP-valid.",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=True), ],
         should = [ dict(tx = alltxes[txid3a], valid=True), ],
         ),
    dict(description = "When SEND splits tokens from MINT, a further SEND should be SLP-invalid since it over-outputs.",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=True), ],
         should = [ dict(tx = alltxes[txid3b], valid=False), ],
         ),
    dict(description = "When SEND splits tokens from MINT, an eventual SEND merging the tokens should be SLP-valid.",
         when   = [ dict(tx = alltxes[txid1], valid=True), dict(tx = alltxes[txid2], valid=True), dict(tx = alltxes[txid3a], valid=True), dict(tx = alltxes[txid4], valid=True), ],
         should = [ dict(tx = alltxes[txid5], valid=True), ],
         ),
    ])


txid1 = maketx([
                 mkinput(genesis_txid, 2)
                ],
               [
                 slp.buildMintOpReturnOutput_V1(genesis_txid, 2, 100),
                 (TYPE_ADDRESS, bob, 546),
                 (TYPE_ADDRESS, bob, 546),
                ])

txid2 = maketx([
                 mkinput(txid1, 2)
                ],
               [
                 slp.buildMintOpReturnOutput_V1(genesis_txid, 2, 100),
                 (TYPE_ADDRESS, bob, 546),
                 (TYPE_ADDRESS, bob, 546),
                ])

txid2a = maketx([
                 mkinput(txid1, 2)
                ],
               [
                 slp.buildMintOpReturnOutput_V2(genesis_txid, 2, 100),
                 (TYPE_ADDRESS, bob, 546),
                 (TYPE_ADDRESS, bob, 546),
                ])

tests.extend([
    dict(description = "When MINT spends baton to another MINT baton, should be SLP-valid.",
         when   = [ dict(tx = alltxes[txid1], valid=True)],
         should = [ dict(tx = alltxes[txid2], valid=True), ],
         ),
     dict(description = "When MINT spends baton to another MINT baton, should be SLP-invalid due to invalid baton parent.",
         when   = [ dict(tx = alltxes[txid1], valid=False)],
         should = [ dict(tx = alltxes[txid2], valid=False), ],
         ),
     dict(description = "When MINT spends baton to another MINT baton, should be SLP-invalid due to token version/type mismatch.",
         when   = [ dict(tx = alltxes[txid1], valid=True)],
         should = [ dict(tx = alltxes[txid2a], valid=False), ],
         ),
     ])


with open('tx_input_tests.json', 'w') as f:
    json.dump(tests, f, indent=1)
