import base58
import logging
import logging.config
import os
import time
from collections import defaultdict
from typing import Dict, Optional

from flask import Flask, Response, send_from_directory, request
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.core import RPCException

import zebecstreamer.zebec as zebec

app = Flask(__name__)
log = logging.getLogger(__name__)

lamports_received: Dict[str, int] = defaultdict(lambda: 0)
data_rate = 100  # lamports per second
withdrawal_period = 10 # attempt withdrawal every 10 seconds

mykeypair = Keypair.from_secret_key(
    base58.b58decode(os.getenv("ZSTREAM_SECRET_KEY"))
)

@app.route("/stream")
def stream():
    datarate = 24000 / 8
    buffer = 16384

    sender_pubstr = request.args.get("sender")
    pda_pubstr = request.args.get("pda")
    sender = PublicKey(sender_pubstr)
    pda = PublicKey(pda_pubstr)

    def generator():
        log.info("Starting up generator")
        stream_starttime: float = time.time()
        validated_starttime: Optional[float] = None
        last_withdrawal: Optional[float] = None
        readbytes = 0
        fp_validated = open("input.mp3", 'rb')
        fp_invalid = open('invalid.mp3', 'rb')
        while True:
            if validated_starttime is None:
                log.info("Validated stream not yet started")
                lamports_needed = withdrawal_period * data_rate
            else:
                lamports_needed = (time.time() - validated_starttime) * data_rate
            log.info(f"Lamports needed: {lamports_needed}")
            if lamports_received[sender_pubstr] < lamports_needed:
                log.info(f"Insufficient funds ({lamports_received[sender_pubstr]})")
                if last_withdrawal is None or time.time() - last_withdrawal > 10:
                    log.info(f"Attempting withdrawal of {int(2*lamports_needed)} lamports")
                    try:
                        last_withdrawal = time.time()
                        zebec.withdrawNativeTransaction(
                            sender,
                            mykeypair,
                            pda,
                            int(2*lamports_needed)
                        )
                    except RPCException:
                        # insufficient funds
                        log.exception("Withdrawal failed")
                        fp = fp_invalid
                    else:
                        log.info("Withdrawal succeeded")
                        lamports_received[sender_pubstr] += 2*lamports_needed
                        validated_starttime = time.time()
                        fp = fp_validated
                else:
                    fp = fp_invalid
            else:
                log.info("User has sufficient funds to continue")
                fp = fp_validated
            data = fp.read(1024)
            expected = (time.time() - stream_starttime) * datarate + buffer
            log.info(f'Expected {expected} bytes, currently at {readbytes}')
            if readbytes > expected:
                waittime = (readbytes - expected) / datarate
                log.info(f'Have read more data than needed, waiting {waittime} seconds')
                time.sleep(waittime)
            yield data
            readbytes += len(data)
    return Response(generator(), mimetype="audio/mpeg")


# @app.route("/")
# def player():
#     return send_from_directory("static", "index.html")


def setuplogging():
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout',
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console'],
        }
    }
    logging.config.dictConfig(config)


# def initkeypair():
#     client = Client(zebec.devnet_url)
#     log.info("Target ")


if __name__ == "__main__":
    setuplogging()
    log.info(f"Target public key is {mykeypair.public_key}")
    app.run(debug=True)

