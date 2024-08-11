import React, { useState } from 'react';
import ChatbotComponent from '../components/Chatbot/Chatbot';
import AvatarComponent from '../components/AvatarComponent';
import GoogleMapComponent from '@/components/googlemap';

const Home: React.FC = () => {
  const [messages, setMessages] = useState<any[]>([]);
  const [center, setCenter] = useState({ lat: 37.619380950927734, lng: -122.38162994384766 });
  const [mapMarkers, setMapMarkers] = useState<any[]>([]);
  const [imgSrc, setImgSrc] = useState<string>(""); // 追加

  return (
      <main>
        <div className="container">
          <div className="left-container">
            <div className='avatar-container'>
              <AvatarComponent />
            </div>
          </div>
          <div className="chat-container">
            <ChatbotComponent
              messages={messages}
              setCenter={setCenter}
              setMapMarkers={setMapMarkers}
              setImgSrc={setImgSrc} // 追加
            />
          </div>
          <div className="right-container">
            <GoogleMapComponent center={center} markers={mapMarkers} />
            <div className="photo-box">
              <img src={imgSrc} alt="Floor Layout" />
            </div>
          </div>
        </div>
      </main>
  );
};

export default Home;
