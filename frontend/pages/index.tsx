import React, { useState } from 'react';
import Head from 'next/head';
import ChatbotComponent from '../components/Chatbot/Chatbot';

const Home: React.FC = () => {
  const [messages, setMessages] = useState<any[]>([]);

  const handleUserInput = async (userInput: string) => {
    // Add the user input to the messages
    setMessages([...messages, { type: 'user', text: userInput }]);

    // Call the API
    const response = await fetch('/api/bedrock', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ input: userInput }),
    });

    const data = await response.json();

    // Add the response to the messages
    setMessages([...messages, { type: 'user', text: userInput }, { type: 'bot', text: data.response }]);
  };

  return (
    <div className="container">
      <Head>
        <title>AI Apartment Concierge</title>
        <meta name="description" content="AI Concierge for finding the perfect apartment" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="chat-box">
        <h1>AI Apartment Concierge</h1>
        <ChatbotComponent messages={messages} onUserInput={handleUserInput} />
      </main>
    </div>
  );
};

export default Home;
