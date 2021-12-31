import struct

from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta, Transaction
from solana.rpc.api import Client
from solana.rpc.commitment import Finalized, Confirmed
from solana.keypair import Keypair

base58publickey = PublicKey('7FNWTfCo3AyRBFCvr49daqKHehdn2GjNgpjuTsqy5twk')
stringofwithdraw = "withdraw_sol"
systemprogramid = "11111111111111111111111111111111"
zebecprogramid = "7FNWTfCo3AyRBFCvr49daqKHehdn2GjNgpjuTsqy5twk"
devnet_url = "https://api.devnet.solana.com"
client = Client(devnet_url)
lamportspersol = 1000000000


def withdrawNativeTokenDeposit(sender: Keypair, lamports: int):
    program_addr_pub = PublicKey.find_program_address(
        [sender.public_key.to_base58()],
        base58publickey
    )
    program_addr = program_addr_pub[0].to_base58()
    withdraw_data = PublicKey.find_program_address(
        [stringofwithdraw.encode('utf-8'), bytes(sender.public_key)],
        base58publickey
    )
    instruction = TransactionInstruction(
        [
            AccountMeta(sender.public_key, True, True),
            AccountMeta(PublicKey(program_addr.decode('utf-8')), False, True),
            AccountMeta(PublicKey(withdraw_data[0].to_base58().decode('utf-8')), False, True),
            AccountMeta(PublicKey(systemprogramid), False, False),
        ],
        PublicKey(zebecprogramid),
        encodeNativeWithdrawDepositInstructionData(lamports)
    )
    transaction = Transaction().add(instruction)
    transaction.recent_blockhash = client.get_recent_blockhash().get('result')['value']['blockhash'].encode('utf-8')
    transaction.fee_payer = sender.public_key
    transaction.sign(sender)
    signature = client.send_raw_transaction(transaction.serialize()).get('result')
    client.confirm_transaction(signature, Finalized)
    if signature is not None:
        return signature


def withdrawNativeTransaction(
        sender: PublicKey,
        receiver: Keypair,
        pda: PublicKey,
        lamports: int
):
    program_addr_pub = PublicKey.find_program_address(
        [bytes(sender)], base58publickey
    )
    validProgramAddr: PublicKey = program_addr_pub[0]
    withdraw_data = PublicKey.find_program_address(
        [stringofwithdraw.encode('utf-8'), bytes(sender)],
        base58publickey
    )
    instruction = TransactionInstruction(
        [
            AccountMeta(sender, False, True),
            AccountMeta(receiver.public_key, True, True),
            AccountMeta(validProgramAddr, False, True),
            AccountMeta(pda, False, True),
            AccountMeta(withdraw_data[0], False, True),
            AccountMeta(PublicKey(systemprogramid), False, False),
        ],
        PublicKey(zebecprogramid),
        encodeWithdrawNativeInstructionData(lamports)
    )
    transaction = Transaction().add(instruction)
    transaction.recent_blockhash = client.get_recent_blockhash()['result']['value']['blockhash'].encode('utf-8')
    transaction.fee_payer = receiver.public_key
    transaction.sign(receiver)
    signature = client.send_raw_transaction(transaction.serialize())['result']
    client.confirm_transaction(signature, Finalized)
    return signature


def depositNativeToken(
        sender: Keypair,
        lamports: int
):
    validProgramAddress_pub = PublicKey.find_program_address(
        [bytes(sender.public_key)],
        base58publickey
    )
    validProgramAddress = validProgramAddress_pub[0]
    instruction = TransactionInstruction(
        [
            AccountMeta(sender.public_key, True, True),
            AccountMeta(validProgramAddress, False, True),
            AccountMeta(PublicKey(systemprogramid), False, False),
        ],
        PublicKey(zebecprogramid),
        encodeNativeInstructionData(lamports)
    )
    transaction = Transaction().add(instruction)
    transaction.recent_blockhash = getRecentBlockhash()
    transaction.fee_payer = sender.public_key
    # transaction.sign(mykeypair)
    # signature = client.send_raw_transaction(transaction.serialize())['result']
    signature = client.send_transaction(transaction, sender)['result']
    client.confirm_transaction(signature, Finalized)
    return signature


def initNativeTransaction(
        sender: Keypair,
        receiver: PublicKey,
        lamports: int,
        starttime: int,
        endtime: int,
):
    withdraw_data = PublicKey.find_program_address(
        [stringofwithdraw.encode('utf-8'), bytes(sender.public_key)],
        base58publickey
    )
    pda = Keypair()
    instruction = TransactionInstruction(
        [
            AccountMeta(sender.public_key, True, True),
            AccountMeta(receiver, False, True),
            AccountMeta(pda.public_key, True, True),
            AccountMeta(withdraw_data[0], False, True),
            AccountMeta(PublicKey(systemprogramid), False, False),
        ],
        PublicKey(zebecprogramid),
        encodeInitNativeInstructionData(lamports, starttime, endtime),
    )
    transaction = Transaction().add(instruction)
    transaction.recent_blockhash = getRecentBlockhash()
    transaction.fee_payer = sender.public_key
    signature = client.send_transaction(transaction, sender, pda)['result']
    client.confirm_transaction(signature, Confirmed)
    return {'transactionhash': signature, 'pda': pda.public_key.to_base58()}


def encodeInitNativeInstructionData(
        lamports: int,
        starttime: int,
        endtime: int,
):
    return struct.pack(
        '<BQQQ',
        0,
        starttime,
        endtime,
        lamports,
    )


def getRecentBlockhash():
    return (
        client.get_recent_blockhash()
            ['result']
            ['value']
            ['blockhash']
            .encode('utf-8')
    )


def encodeNativeInstructionData(lamports: int):
    return struct.pack('<BQ', 7, lamports)


def encodeNativeWithdrawDepositInstructionData(lamports: int) -> bytes:
    return struct.pack('<BQ', 14, lamports)

def encodeWithdrawNativeInstructionData(lamports: int) -> bytes:
    return struct.pack('<BQ', 1, lamports)
