import React, { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import styles from './ChatbotComponent.module.css';

declare global {
  interface Window {
    setChatHistory: () => void;
  }
}

interface ChatbotComponentProps {
  messages: any[];
  setCenter: React.Dispatch<React.SetStateAction<{ lat: number; lng: number }>>;
  setMapMarkers: React.Dispatch<React.SetStateAction<any[]>>;
  setImgSrc: React.Dispatch<React.SetStateAction<string>>; // 追加
}

const ChatbotComponent: React.FC<ChatbotComponentProps> = ({ messages, setCenter, setMapMarkers, setImgSrc }) => {
  const [userInput, setUserInput] = useState('');
  const [chatHistory, setChatHistory] = useState<any[]>([]);
  const [socket, setSocket] = useState<WebSocket | null>(null);

  // `updateChatHistory`関数を定義
  const updateChatHistory = (newMessage: any) => {
    setChatHistory((prevHistory) => {
      const updatedHistory = [...prevHistory, newMessage];
  
      // window.setChatHistoryが存在するか確認して呼び出す
      if (window.setChatHistory) {
        window.setChatHistory();
      }
  
      return updatedHistory;
    });
  };

  useEffect(() => {
    const id = uuidv4();
    sessionStorage.setItem('sessionId', id);
    const newSocket = new WebSocket('ws://localhost:8080/ws');
    setSocket(newSocket);

    newSocket.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      console.log('Received message:', data);

      if (data.response_obj) {
        const { name, price, beds, location, imgSrc, detailUrl } = data.response_obj;

        const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;
        const geocodeResponse = await fetch(`https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(location)}&key=${apiKey}`);
        const geocodeData = await geocodeResponse.json();

        if (geocodeData.results && geocodeData.results.length > 0) {
          const { lat, lng } = geocodeData.results[0].geometry.location;
          console.log(`Location coordinates: Latitude - ${lat}, Longitude - ${lng}`);

          setMapMarkers((prevMarkers) => [
            ...prevMarkers,
            { id: uuidv4(), name, position: { lat, lng } }
          ]);

          setCenter({ lat, lng });
        }

        setImgSrc(imgSrc); // imgSrcをHomeコンポーネントに渡す
        if (name) {
          updateChatHistory({ sender: 'Operator', text: `Name: ${name}\nPrice: ${price}\nBeds: ${beds}\nLocation: ${location}` });
          updateChatHistory({ sender: 'Operator', text: `${detailUrl}` });
        }

      } else {
        updateChatHistory({ sender: 'Operator', text: data.message });
      }
    };

    newSocket.onclose = () => {
      console.log('WebSocket connection closed');
    };
    return () => newSocket.close();
  }, [setCenter, setMapMarkers, setImgSrc]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!userInput.trim()) return;
    const userMessage = { sender: 'User', text: userInput };
    
    if (socket) {
      socket.send(JSON.stringify({ user_input: userInput }));
    }
    
    updateChatHistory(userMessage); // ユーザー入力時にもチャット履歴を更新
    
    setUserInput('');
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setUserInput(event.target.value);
  };

  useEffect(() => {
    const initialMessage = { sender: 'Operator', text: 'Hi, I am Moxie, AI Apartment Concierge. How can I help you?' };
    updateChatHistory(initialMessage); // アニメーションをトリガー
  }, []);

  return (
    <div className={styles.chatBox}>
      <div className={styles.chatContainer}>
        {chatHistory.map((chat, index) => (
          <div
            key={index}
            className={`${styles.chatBubble} ${chat.sender === 'User' ? styles.userBubble : styles.operatorBubble}`}
          >
            {chat.text.split('\n').map((line, i) => (
              <React.Fragment key={i}>
                {line}
                <br />
              </React.Fragment>
            ))}
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className={styles.chatForm}>
        <input
          type="text"
          value={userInput}
          onChange={handleInputChange}
          placeholder="Type your message..."
          className={styles.chatInput}
        />
        <button type="submit" className={styles.sendButton}>Send</button>
      </form>
    </div>
  );
};

export default ChatbotComponent;
