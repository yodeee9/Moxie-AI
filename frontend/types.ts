export interface ApartmentInfo {
    name: string;
    price: string;
    beds: string;
    address: string;
    imgSrc: string;
    detailUrl: string;
    coordinates?: { lat: number; lng: number };
    reason?: string;
  }