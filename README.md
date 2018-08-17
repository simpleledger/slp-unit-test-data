# slp-unit-test-data
Test vectors for ensuring that validators of the Simple Ledger Protocol follow consensus.


# Parsing of OP_RETURN scripts

**File: [script_tests.json](script_tests.json)**

The SLP specification demands a number of very particular formatting requirements on the OP_RETURN script. It is absolutely essential that every implementation is on the same page with parsing

[script_tests.json](script_tests.json) includes a series of script examples and the expected pass/fail result. For every script entry, there is a human-readable 'msg' that explains the point of the test and whether it must pass or must fail. The `code` attribute is `null` for all valid messages, and otherwise is an integer representing a failure mode.

Note that it is not required for consensus that implementations agree on the reason, however unit tests should use this code to make sure the invalidation reason matches the expected result.

Overall script error codes:
* 1 - Basic error that prevents even parsing as a bitcoin script (currently, only for truncated scripts).
* 2 - Disallowed opcodes (after OP_RETURN, only opcodes 0x01 - 0x4e may be used).
* 3 - Not an SLP message (script is not OP_RETURN, or ). Note in some implementations, the parsers would never be given such non-SLP scripts in the first place. In such implementations, error code 3 tests may be skipped as they are not relevant.

Reasons relating to the specified limits:
* 10 - A push chunk has the wrong size.
* 11 - A push chunk has an illegal value.
* 12 - A push chunk is missing / there are too few chunks.

Specific to one particular transaction type:

* 21 - Too many optional values (currently, only if there are more than 19 token output amounts)

Other:
* 255 - The SLP token_type field is has an unsupported value. Depending on perspective this is not 'invalid' per se -- it simply cannot be parsed since the protocol for that token_type is not known. Like error code 3 these tests may not be applicable to some parsers.


# Transaction input tests

These tests involve providing raw transactions A,B,C,D,... that form inputs to transaction T. The SLP validity judgement (valid/invalid) of A,B,C,D,... is given as a test assumption, and the test is to determine the validity of T.

(to be expanded and created)
