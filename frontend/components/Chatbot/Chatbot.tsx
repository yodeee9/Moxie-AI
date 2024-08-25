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
  setImgSrc: React.Dispatch<React.SetStateAction<string>>;
  apartments: ApartmentInfo[];
  setApartments: React.Dispatch<React.SetStateAction<ApartmentInfo[]>>;
  onApartmentClick: (apartmentInfo: ApartmentInfo) => void;
}

interface ApartmentInfo {
  name: string;
  price: string;
  beds: string;
  address: string;
  imgSrc: string;
  detailUrl: string;
  coordinates?: { lat: number; lng: number };
  reason: string;
}


const ChatbotComponent: React.FC<ChatbotComponentProps> = ({ 
  messages,
  setCenter,
  setMapMarkers,
  setImgSrc,
  apartments,
  setApartments,
  onApartmentClick
 }) => {
  const [userInput, setUserInput] = useState('');
  const [chatHistory, setChatHistory] = useState<any[]>([]);
  const [socket, setSocket] = useState<WebSocket | null>(null);

  const updateChatHistory = (newMessage: any) => {
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

      if (data.response_obj) {
        const { name, price, beds, address, imgSrc, detailUrl, reason, latitude, longitude } = data.response_obj;

        // const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;
        // const geocodeResponse = await fetch(`https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(location)}&key=${apiKey}`);
        // const geocodeData = await geocodeResponse.json();

        // let coordinates;
        // if (geocodeData.results && geocodeData.results.length > 0) {
        //   console.log('Geocode data:', geocodeData.results[0]);
        //   coordinates = geocodeData.results[0].geometry.location;
        // }

        const coordinates = { lat: latitude, lng: longitude };
        console.log('Coordinates:', coordinates);

        const newApartment: ApartmentInfo = { name, price, beds, address, imgSrc, detailUrl, coordinates, reason };
        setApartments(prevApartments => [...prevApartments, newApartment]);

        updateChatHistory({ 
          sender: 'Operator', 
          text: `- Name: ${name}\n- Price: ${price}\n- Beds: ${beds}\n- Recommend Reason: ${reason}\n- URL: ${detailUrl}`,
          apartmentInfo: newApartment
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
    const userMessage = { sender: 'User', text: userInput };
    
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
    const initialMessage = { sender: 'Operator', text: 'Hi, I am Moxie, AI Apartment Concierge. How can I help you?' };
    updateChatHistory(initialMessage);
  }, []);

  return (
    <div className={styles.chatBox}>
      <div className={styles.chatContainer}>
        {chatHistory.map((chat, index) => (
          <div
          key={index}
          className={`${styles.chatBubble} ${chat.sender === 'User' ? styles.userBubble : styles.operatorBubble} ${chat.apartmentInfo ? styles.clickable : ''}`}
          onClick={() => chat.apartmentInfo && handleApartmentClick(chat.apartmentInfo)}
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
