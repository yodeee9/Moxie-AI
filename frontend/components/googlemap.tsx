import React from 'react';
import { GoogleMap, LoadScript, Marker } from '@react-google-maps/api';

interface MapMarker {
  id: string;
  name: string;
  position: { lat: number; lng: number };
}

interface GoogleMapComponentProps {
  center: { lat: number; lng: number };
  markers: MapMarker[];
}

const mapContainerStyle = {
  width: '350px',
  height: '350px',
};


const GoogleMapComponent: React.FC<GoogleMapComponentProps> = ({ center, markers }) => {
  return (
    <LoadScript googleMapsApiKey={process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || ''} language='en'>
      <GoogleMap
        mapContainerStyle={mapContainerStyle}
        center={center}
        zoom={12}
      >
        {markers.map(marker => (
          <Marker key={marker.id} position={marker.position} label={marker.name} />
        ))}
      </GoogleMap>
    </LoadScript>
  );
};

export default GoogleMapComponent;
