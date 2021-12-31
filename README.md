# zebec-music

This is a proof of concept for a paid streaming service that is paid for over a continuous
settlement protocol, zebec. It contains a simple mock streaming backend, `pystreamer`, that
takes two mp3s as input - one that plays if the stream is being paid for, and another that
plays if no payment stream exists, or the funds being transferred are insufficient; and a
simple NextJs frontend.

To run it, create a virtual environment and run `pip install -r requirements.txt`, set
the environment variable `ZSTREAM_SECRET_KEY` to a base58 encoded secret key, and run
`python streamer.py`. Then update the front-end to point to the correct public key for the
backend, run `npm build`, and `npm run dev`.
