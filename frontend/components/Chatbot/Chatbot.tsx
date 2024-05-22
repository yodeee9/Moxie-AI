import React, { useState, useEffect } from 'react';
import Chatbot from 'react-chatbot-kit';
import 'react-chatbot-kit/build/main.css';
import { v4 as uuidv4 } from 'uuid';
import styles from './Chatbot.module.css';

import config from './config';
import MessageParser from './MessageParser';
import ActionProvider from './ActionProvider';

const ChatbotComponent: React.FC = () => {
  const [messages, setMessages] = useState<any[]>([]);
  const [sessionId, setSessionId] = useState<string>('');

  useEffect(() => {
    const id = uuidv4();
    setSessionId(id);
    sessionStorage.setItem('sessionId', id); // Store sessionId in sessionStorage
  }, []);

  return (
    <div className={styles.chatbotContainer}>
      <Chatbot
        config={config}
        messageParser={MessageParser}
        actionProvider={ActionProvider}
        messages={messages}
      />
    </div>
  );
};

export default ChatbotComponent;
