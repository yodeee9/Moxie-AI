// pages/_app.tsx

import Header from '@/components/Header';
import '../styles/globals.css';
import { AppProps } from 'next/app';
import 'regenerator-runtime/runtime';

function MyApp({ Component, pageProps }: AppProps) {
  return (
  <div>
    <header>
      <Header />
    </header>
   <Component {...pageProps} />)
  </div>
  );
}

export default MyApp;
