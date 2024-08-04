import React, { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import styles from './ChatbotComponent.module.css'; 

const ChatbotComponent: React.FC = () => {
  const [userInput, setUserInput] = useState('');
  const [chatHistory, setChatHistory] = useState<any[]>([]);
  const { transcript, resetTranscript } = useSpeechRecognition();
  const [socket, setSocket] = useState<WebSocket | null>(null);

  useEffect(() => {
    const id = uuidv4();
    sessionStorage.setItem('sessionId', id);

    // WebSocketの初期設定
    const newSocket = new WebSocket('ws://localhost:8080/ws');
    setSocket(newSocket);

    newSocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setChatHistory((prevHistory) => [...prevHistory, { sender: 'Operator', text: data.message }]);
    };

    newSocket.onclose = () => {
      console.log('WebSocket connection closed');
    };

    return () => newSocket.close();
  }, []);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!userInput.trim()) return;

    const userMessage = { sender: 'User', text: userInput };
    setChatHistory((prevHistory) => [...prevHistory, userMessage]);

    if (socket) {
      socket.send(JSON.stringify({ user_input: userInput }));
    }

    setUserInput('');
    resetTranscript();
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setUserInput(event.target.value);
  };

  useEffect(() => {
    const initialMessage = { sender: 'Operator', text: 'May I help you?' };
    setChatHistory([initialMessage]);
  }, []);

  return (
    <div className={styles.chatBox}>
      <div className={styles.chatContainer}>
        {chatHistory.map((chat, index) => (
          <div key={index} className={styles.chatMessage}><strong>{chat.sender}:</strong> {chat.text}</div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className={styles.chatForm}>
        <input
          type="text"
          value={userInput}
          onChange={handleInputChange}
          placeholder="Type your message..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
};

export default ChatbotComponent;
