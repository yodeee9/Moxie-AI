import React, { useState } from 'react';
import ChatbotComponent from '../components/Chatbot/Chatbot';
import AvatarComponent from '../components/AvatarComponent';
import GoogleMapComponent from '@/components/googlemap';
import Calendar from 'react-calendar';


interface ApartmentInfo {
  name: string;
  price: string;
  beds: string;
  location: string;
  imgSrc: string;
  detailUrl: string;
  coordinates?: { lat: number; lng: number };
}

const Home: React.FC = () => {
  type ValuePiece = Date | null;
  type Value = ValuePiece | [ValuePiece, ValuePiece];
  const [messages, setMessages] = useState<any[]>([]);
  const [center, setCenter] = useState({ lat: 37.619380950927734, lng: -122.38162994384766 });
  const [mapMarkers, setMapMarkers] = useState<any[]>([]);
  const [imgSrc, setImgSrc] = useState<string>("");
  const [apartments, setApartments] = useState<ApartmentInfo[]>([]);
  const [value, onChange] = useState<Value>(new Date());

  const handleApartmentClick = (apartmentInfo: ApartmentInfo) => {
    if (apartmentInfo.coordinates) {
      setCenter(apartmentInfo.coordinates);
      setMapMarkers([{ id: Date.now().toString(), name: apartmentInfo.name, position: apartmentInfo.coordinates }]);
    }
    setImgSrc(apartmentInfo.imgSrc);
  };

  return (
    <main>
      <div className="container">
        <div className="left-container">
          <div className='avatar-container'>
            <AvatarComponent />
          </div>
          {/* <div className="calendar-container">
            <Calendar onChange={onChange} value={value} />
          </div> */}
        </div>
        <div className="chat-container">
          <ChatbotComponent
            messages={messages}
            setCenter={setCenter}
            setMapMarkers={setMapMarkers}
            setImgSrc={setImgSrc}
            apartments={apartments}
            setApartments={setApartments}
            onApartmentClick={handleApartmentClick}
          />
        </div>
        <div className="right-container">
          <GoogleMapComponent center={center} markers={mapMarkers} />
          <div className="photo-box">
            <img src={imgSrc} alt="Apartment Image" />
          </div>
        </div>
      </div>
    </main>
  );
};

export default Home;