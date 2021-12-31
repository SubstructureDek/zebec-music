import logging
import time

from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc.commitment import Finalized

import zebecstreamer.zebec as zebec

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def test_streaming():
    keypair1 = Keypair()
    keypair2 = Keypair()
    client = Client(zebec.devnet_url)
    log.info("Requesting airdrop")
    resp = client.request_airdrop(keypair1.public_key, 15000000)
    client.confirm_transaction(resp['result'], Finalized)
    log.info("Depositing tokens")
    zebec.depositNativeToken(keypair1, 10000000)
    starttime = int(time.time() + 10)
    endtime = starttime + 10
    log.info("Initializing stream")
    result = zebec.initNativeTransaction(
        keypair1, keypair2.public_key, 5000000, starttime, endtime
    )
    pda = PublicKey(result['pda'].decode('utf-8'))
    log.info("Waiting for stream to finish")
    for ind in range(20):
        print(client.get_account_info(keypair2.public_key))
        time.sleep(1.0)
    log.info("Withdrawing funds")
    import ipdb; ipdb.set_trace()
    zebec.withdrawNativeTransaction(
        keypair1.public_key,
        keypair2,
        pda,
        50000
    )
    print(client.get_account_info(keypair1.public_key))
    print(client.get_account_info(keypair2.public_key))


if __name__ == '__main__':
    test_streaming()
