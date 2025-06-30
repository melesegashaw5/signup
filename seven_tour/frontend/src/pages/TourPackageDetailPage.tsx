import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getTourPackageById, TourPackage } from '../services/apiService'; // Assuming interfaces are here

const TourPackageDetailPage: React.FC = () => {
  const [tourPackage, setTourPackage] = useState<TourPackage | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { id } = useParams<{ id: string }>(); // Get ID from URL parameters

  useEffect(() => {
    if (!id) {
      setError("No package ID provided.");
      setLoading(false);
      return;
    }

    const fetchPackageDetails = async () => {
      setLoading(true);
      setError(null);
      try {
        const numericId = parseInt(id, 10);
        if (isNaN(numericId)) {
          setError("Invalid package ID format.");
          setLoading(false);
          return;
        }
        const data = await getTourPackageById(numericId);
        setTourPackage(data);
      } catch (err) {
        setError('Failed to fetch package details.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchPackageDetails();
  }, [id]);

  if (loading) return <p>Loading package details...</p>;
  if (error) return <p style={{ color: 'red' }}>Error: {error}</p>;
  if (!tourPackage) return <p>Tour package not found.</p>;

  const placeholderImage = "https://via.placeholder.com/600x400?text=Tour+Package+Detail";
  const imageUrl = tourPackage.main_image ? tourPackage.main_image : placeholderImage;

  return (
    <div style={{ padding: '20px' }}>
      <h2>{tourPackage.title}</h2>
      <img src={imageUrl} alt={tourPackage.title} style={{ maxWidth: '100%', height: 'auto', maxHeight: '400px', marginBottom: '20px' }} />

      <p><strong>Country:</strong> {tourPackage.country?.name || 'N/A'}</p>

      {tourPackage.destinations && tourPackage.destinations.length > 0 && (
        <div>
          <strong>Destinations:</strong>
          <ul>
            {tourPackage.destinations.map(dest => <li key={dest.id}>{dest.name}</li>)}
          </ul>
        </div>
      )}

      <p><strong>Visa Requirement:</strong> {tourPackage.visa_type_display}</p>
      <p><strong>Price:</strong> {tourPackage.price} ETB (example currency)</p>
      <p><strong>Duration:</strong> {tourPackage.duration_days ? `${tourPackage.duration_days} days` : 'N/A'}</p>

      <h3>Description:</h3>
      <p>{tourPackage.description || 'No description available.'}</p>

      {tourPackage.highlights && (
        <>
          <h3>Highlights:</h3>
          <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>{tourPackage.highlights}</pre>
        </>
      )}

      {tourPackage.inclusions && (
        <>
          <h3>Inclusions:</h3>
          <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>{tourPackage.inclusions}</pre>
        </>
      )}

      {tourPackage.exclusions && (
        <>
          <h3>Exclusions:</h3>
          <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>{tourPackage.exclusions}</pre>
        </>
      )}

      <p><small>Package listed on: {new Date(tourPackage.created_at).toLocaleDateString()}</small></p>

      {/* Add to cart / booking button would go here */}
      <button onClick={() => alert('Booking functionality not yet implemented!')}>Book Now (Placeholder)</button>
    </div>
  );
};

export default TourPackageDetailPage;
