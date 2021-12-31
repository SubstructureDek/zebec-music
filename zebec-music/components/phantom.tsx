import {Dispatch, FunctionComponent, SetStateAction} from "react"
import {
    PublicKey,
    Keypair,
    Transaction,
    TransactionInstruction,
    LAMPORTS_PER_SOL,
    SystemProgram,
    Connection,
    clusterApiUrl,
} from "@solana/web3.js"
import BufferLayout from "buffer-layout"
import {u64} from "@solana/spl-token"

// import {initNativeTransaction} from "zebecprotocol-sdk"

const base58publicKey = new PublicKey(
    "7FNWTfCo3AyRBFCvr49daqKHehdn2GjNgpjuTsqy5twk"
);
let stringofwithdraw = "withdraw_sol";
const PROGRAM_ID = "7FNWTfCo3AyRBFCvr49daqKHehdn2GjNgpjuTsqy5twk"; // Zebec program id


type ConnectWalletProps = {
    setSender: Dispatch<SetStateAction<string>>
}
const CLUSTER = "devnet";
const connection = new Connection(clusterApiUrl(CLUSTER)); // cluster

function encodeInitNativeInstructionData(data: { amount: number; start: number; end: number }) {
    const { amount, start, end } = data;
    const layout = BufferLayout.struct([
        BufferLayout.u8("instruction"),
        BufferLayout.blob(8, "start_time"),
        BufferLayout.blob(8, "end_time"),
        BufferLayout.nu64("amount"),
    ]);

    const encoded = Buffer.alloc(layout.span);
    layout.encode(
        {
            instruction: 0,
            start_time: new u64(start).toBuffer(),
            end_time: new u64(end).toBuffer(),
            amount: Math.trunc(amount * LAMPORTS_PER_SOL),
        },
        encoded
    );

    return encoded;
}
async function initNativeTransaction(data: { sender: string; receiver: string; amount: number; start: number; end: number }) {
    const senderaddress = new PublicKey(data.sender);
    let withdraw_data = await PublicKey.findProgramAddress(
        [Buffer.from(stringofwithdraw), senderaddress.toBuffer()],
        base58publicKey
    );
    // return
    const pda = new Keypair();

    const instruction = new TransactionInstruction({
        keys: [
            {
                pubkey: new PublicKey(data.sender),
                isSigner: true,
                isWritable: true,
            },
            {
                pubkey: new PublicKey(data.receiver), //recipient
                isSigner: false,
                isWritable: true,
            },
            {
                pubkey: pda.publicKey,
                isSigner: true,
                isWritable: true,
            },
            {
                pubkey: withdraw_data[0],
                isSigner: false,
                isWritable: true,
            },
            {
                pubkey: SystemProgram.programId, //system program required to make a transfer
                isSigner: false,
                isWritable: false,
            },
        ],
        programId: new PublicKey(PROGRAM_ID),
        data: encodeInitNativeInstructionData(data),
    });
    console.log(instruction)
    const transaction = new Transaction().add(instruction);

    const signerTransac = async () => {
        try {
            transaction.recentBlockhash = (
                await connection.getRecentBlockhash()
            ).blockhash;

            transaction.feePayer = window.solana.publicKey;
            transaction.sign(pda);
            // transaction.sign(mykeypair)
            // const signed = transaction;
            const signed = await window.solana.signTransaction(transaction);
            // const signature = await connection.sendTransaction(signed, [pda, window.solana.publicKey])
            const signature = await connection.sendRawTransaction(signed.serialize());
            const finality = "confirmed";
            await connection.confirmTransaction(signature, finality);
            const explorerhash = {
                transactionhash: signature,
            };

            return explorerhash;
        } catch (e) {
            console.warn(e);
            return {
                transactionhash: null,
            };
        }
    };
    const signer_response = await signerTransac();
    if (signer_response.transactionhash === null) {
        return {
            status: "error",
            message: "An error has occurred.",
            data: null,
        };
    }
    return {
        status: "success",
        message: "Stream Started.",
        data: {
            ...signer_response,
            pda: pda.publicKey.toBase58(),
        },
    };
}

const connectWallet = async (setSender: Dispatch<SetStateAction<string>> ) => {
    const resp = await window.solana.connect();
    const publicKey = resp.publicKey.toString()
    console.log(`Setting public key to ${publicKey}`)
    setSender(publicKey)
}

const ConnectWallet: FunctionComponent<ConnectWalletProps> = (
    {setSender}
) => {
    return (
        <button onClick={() => connectWallet(setSender)}>Connect Wallet</button>
    )
}

type StartStreamProps = {
    sender: string,
    receiver: string,
    setPda: Dispatch<SetStateAction<string>>,
}

const startStream = async (
    sender: string,
    receiver: string,
    setPda: Dispatch<SetStateAction<string>>,
) => {
    const starttime = Math.trunc(Date.now() / 1000)
    console.log(`starting at ${starttime}`)
    const data = {
        sender: sender,
        receiver: receiver,
        amount: .01,
        start: starttime + 1,
        end: starttime + 60*60
    }
    console.log(data)
    const response = await initNativeTransaction(data);
    setPda(response['data']['pda'])
    console.log(`Streaming has started: ${JSON.stringify(response)}`)
}

const StartStream: FunctionComponent<StartStreamProps> = (
    {sender, receiver, setPda}
) => {
    return (
        <button onClick={() => startStream(sender, receiver, setPda)}>Start streaming</button>
    )
}

export {ConnectWallet, StartStream}
