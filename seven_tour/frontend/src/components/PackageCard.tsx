import React from 'react';
import { Link } from 'react-router-dom';
import { TourPackage } from '../services/apiService'; // Assuming TourPackage interface is defined here

interface PackageCardProps {
  tourPackage: TourPackage;
}

const PackageCard: React.FC<PackageCardProps> = ({ tourPackage }) => {
  // A simple fallback image or placeholder if main_image is null
  const placeholderImage = "https://via.placeholder.com/300x200?text=Tour+Package";
  const imageUrl = tourPackage.main_image ? tourPackage.main_image : placeholderImage;

  return (
    <div style={{ border: '1px solid #ddd', margin: '10px', padding: '15px', width: '300px' }}>
      <img src={imageUrl} alt={tourPackage.title} style={{ width: '100%', height: '200px', objectFit: 'cover' }} />
      <h3>{tourPackage.title}</h3>
      <p><strong>Country:</strong> {tourPackage.country?.name || 'N/A'}</p>
      <p><strong>Price:</strong> {tourPackage.price} ETB (example currency)</p>
      <p><strong>Duration:</strong> {tourPackage.duration_days ? `${tourPackage.duration_days} days` : 'N/A'}</p>
      <p><strong>Visa:</strong> {tourPackage.visa_type_display}</p>
      <Link to={`/packages/${tourPackage.id}`}>View Details</Link>
    </div>
  );
};

export default PackageCard;
