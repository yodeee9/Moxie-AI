import React, { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import axios from 'axios';
import styles from './ChatbotComponent.module.css'; 

const ChatbotComponent: React.FC = () => {
  const [userInput, setUserInput] = useState('');
  const [chatHistory, setChatHistory] = useState<any[]>([]);
  const { transcript, resetTranscript } = useSpeechRecognition();

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!userInput.trim()) return;

    const userMessage = { sender: 'User', text: userInput };
    setChatHistory(chatHistory => [...chatHistory, userMessage]);

    try {
      const response = await axios.post('http://localhost:8080/generate_answer', { user_input: userInput });
      console.log('API Response:', response.data);
      const botResponse = { sender: 'Operator', text: response.data.answer };
      setChatHistory(chatHistory => [...chatHistory, botResponse]);
    } catch (error) {
      console.error('Error sending message:', error);
    }

    setUserInput('');
    resetTranscript();
  };

  const handleInputChange = (event) => {
    setUserInput(event.target.value);
  };

  useEffect(() => {
    const id = uuidv4();
    sessionStorage.setItem('sessionId', id);
    // 初期メッセージを設定
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
        {/* <button type="button" onClick={SpeechRecognition.startListening} className="voice-input-button">
          <img src="/mic-icon.png" alt="Microphone" className="voice-icon"/>
        </button> */}
        <button type="submit">Send</button>
      </form>
    </div>
  );
};

export default ChatbotComponent;
