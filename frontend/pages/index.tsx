import React, { useState } from 'react';
import ChatbotComponent from '../components/Chatbot/Chatbot';
import AvatarComponent from '../components/AvatarComponent';
import Header from '../components/Header';

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
      <main>
        <div className="container">
          <div className="avatar-container">
            <AvatarComponent />
            <h1 className="chat-header">AI Apartment Concierge</h1>
          </div>
          <div className="chat-box">
            <ChatbotComponent messages={messages} onUserInput={handleUserInput} />
          </div>
        </div>
      </main>
  );
};

export default Home;
