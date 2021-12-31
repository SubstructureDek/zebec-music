import type { NextPage } from 'next'
import Head from 'next/head'
import Image from 'next/image'
import styles from '../styles/Home.module.css'
import ZebecPlayer from "../components/zebecplayer";
import {useState} from "react";
import {ConnectWallet, StartStream} from "../components/phantom";

const Home: NextPage = () => {
  const [sender, setSender] = useState('11111111111111111111111111111111111111111111')
  const [pda, setPda] = useState('11111111111111111111111111111111111111111111')
  const receiver = '8hTaKhS93AhVWgX7xPo2kK677P1RKp7TnCAX7ZJuMYC4'
  return (
    <div className={styles.container}>
      <Head>
        <title>Zebec Music Demo</title>
        <meta name="description" content="Demo of using Zebec to stream sol to stream music" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <h1 className={styles.title}>
          Zebec Music Demo
        </h1>

        <p className={styles.description}>
          <ZebecPlayer
              url="http://localhost:5000/stream"
              sender={sender}
              pda={pda}
          />
        </p>

        <div className={styles.grid}>
          <a className={styles.card}>
              <ConnectWallet setSender={setSender}/>
              <h6>{sender}</h6>
          </a>

          <a className={styles.card}>
              <StartStream sender={sender} receiver={receiver} setPda={setPda}/>
              <h6>{pda}</h6>
          </a>

        </div>
      </main>

      <footer className={styles.footer}>
        <a
          href="https://vercel.com?utm_source=create-next-app&utm_medium=default-template&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          Powered by{' '}
          <span className={styles.logo}>
            <Image src="/vercel.svg" alt="Vercel Logo" width={72} height={16} />
          </span>
        </a>
      </footer>
    </div>
  )
}

export default Home
