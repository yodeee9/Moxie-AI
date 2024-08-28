import React, { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import styles from './ChatbotComponent.module.css';
import { ApartmentInfo } from '@/types';
declare global {
  interface Window {
    setChatHistory: () => void;
  }
}

interface ChatbotComponentProps {
  messages: any[];
  setCenter: React.Dispatch<React.SetStateAction<{ lat: number; lng: number }>>;
  setMapMarkers: React.Dispatch<React.SetStateAction<any[]>>;
  setImgSrc: React.Dispatch<React.SetStateAction<string>>;
  apartments: ApartmentInfo[];
  setApartments: React.Dispatch<React.SetStateAction<ApartmentInfo[]>>;
  onApartmentClick: (apartmentInfo: ApartmentInfo) => void;
}

interface NewsInfo {
  newsTitle: string;
  source: string;
  newsDescription: string;
  url: string;
}

interface ChatMessage {
  sender: 'User' | 'Operator';
  text: string;
  apartmentInfo?: ApartmentInfo;
  newsInfo?: NewsInfo;
}

const ChatbotComponent: React.FC<ChatbotComponentProps> = ({ 
  setCenter,
  setMapMarkers,
  setImgSrc,
  setApartments,
  onApartmentClick
 }) => {
  const [userInput, setUserInput] = useState('');
  const [chatHistory, setChatHistory] = useState<any[]>([]);
  const [socket, setSocket] = useState<WebSocket | null>(null);

  const updateChatHistory = (newMessage: ChatMessage) => {
    setChatHistory((prevHistory) => {
      const updatedHistory = [...prevHistory, newMessage];
  
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

      if (data.apartment_obj) {
        const { name, price, beds, address, imgSrc, detailUrl, reason, latitude, longitude } = data.apartment_obj;

        const coordinates = { lat: latitude, lng: longitude };
        console.log('Coordinates:', coordinates);

        const newApartment: ApartmentInfo = { name, price, beds, address, imgSrc, detailUrl, coordinates, reason };
        setApartments(prevApartments => [...prevApartments, newApartment]);

        updateChatHistory({ 
          sender: 'Operator', 
          text: `- Name: ${name}\n- Price: ${price}\n- Beds: ${beds}\n- Recommend Reason: ${reason}\n- URL: ${detailUrl}`,
          apartmentInfo: newApartment
        });
      } else if (data.news_obj) {
        const { newsTitle, source, newsDescription, url } = data.news_obj;
        const newsInfo: NewsInfo = { newsTitle, source, newsDescription, url };
        updateChatHistory({ 
          sender: 'Operator', 
          text: 'News Information',
          newsInfo: newsInfo
        });
      } else {
        updateChatHistory({ sender: 'Operator', text: data.message });
      }
    };

    newSocket.onclose = () => {
      console.log('WebSocket connection closed');
    };
    return () => newSocket.close();
  }, [setCenter, setMapMarkers, setImgSrc,setApartments]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!userInput.trim()) return;
    const userMessage: ChatMessage = { sender: 'User', text: userInput };
    
    if (socket) {
      socket.send(JSON.stringify({ user_input: userInput }));
    }
    
    updateChatHistory(userMessage);
    setUserInput('');
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setUserInput(event.target.value);
  };

  const handleApartmentClick = (apartmentInfo: ApartmentInfo) => {
    if (apartmentInfo.coordinates) {
      setCenter(apartmentInfo.coordinates);
      setMapMarkers([{ id: uuidv4(), name: apartmentInfo.name, position: apartmentInfo.coordinates }]);
    }
    setImgSrc(apartmentInfo.imgSrc);
  };

  useEffect(() => {
    const initialMessage: ChatMessage = { sender: 'Operator', text: 'Hi, I am Moxie, AI Apartment Concierge. How can I help you?' };
    updateChatHistory(initialMessage);
  }, []);


  const renderMessage = (message: ChatMessage, index: number) => {
    if (message.apartmentInfo) {
      return (
        <div
          key={index}
          className={`${styles.chatBubble} ${styles.operatorBubble} ${styles.apartmentCard}`}
          onClick={() => onApartmentClick(message.apartmentInfo!)}
        >
          <table className={styles.apartmentTable}>
            <tbody>
              <tr><th>Name:</th><td>{message.apartmentInfo.name}</td></tr>
              <tr><th>Price:</th><td>${message.apartmentInfo.price}</td></tr>
              <tr><th>Beds:</th><td>{message.apartmentInfo.beds}</td></tr>
              <tr><th>Reason:</th><td>{message.apartmentInfo.reason}</td></tr>
              <tr>
                <th>URL:</th>
                <td>
                  <a href={message.apartmentInfo.detailUrl} target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()}>
                    View on Zillow
                  </a>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      );
    } else if (message.newsInfo) {
      return (
        <div
          key={index}
          className={`${styles.chatBubble} ${styles.operatorBubble} ${styles.newsCard}`}
        >
          <table className={styles.newsTable}>
            <tbody>
              <tr><th>Title:</th><td>{message.newsInfo.newsTitle}</td></tr>
              <tr><th>Source:</th><td>{message.newsInfo.source}</td></tr>
              <tr><th>Description:</th><td>{message.newsInfo.newsDescription}</td></tr>
              <tr>
                <th>URL:</th>
                <td>
                  <a href={message.newsInfo.url} target="_blank" rel="noopener noreferrer">
                    Read More
                  </a>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      );
    } else {
      return (
        <div
          key={index}
          className={`${styles.chatBubble} ${message.sender === 'User' ? styles.userBubble : styles.operatorBubble}`}
        >
          {message.text}
        </div>
      );
    }
  };

  return (
    <div className={styles.chatBox}>
      <div className={styles.chatContainer}>
        {chatHistory.map((message, index) => renderMessage(message, index))}
      </div>
      <form onSubmit={handleSubmit} className={styles.chatForm}>
        <input
          type="text"
          value={userInput}
          onChange={handleInputChange}
          placeholder="Type your message..."
          className={styles.chatInput}
        />
        <button type="submit" className={styles.sendButton}>
          <img src="send_button2.svg" alt="Button Icon"></img>
        </button>
      </form>
    </div>
  );
};

export default ChatbotComponent;
