import React, { useState, useEffect, useCallback } from 'react';
import { getTourPackages, TourPackage, Country, getCountries, PaginatedResponse } from '../services/apiService';
import PackageCard from '../components/PackageCard'; // Assuming PackageCard component exists

const TourPackagesListPage: React.FC = () => {
  const [packages, setPackages] = useState<TourPackage[]>([]);
  const [countries, setCountries] = useState<Country[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters and Pagination State
  const [selectedCountry, setSelectedCountry] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [sortBy, setSortBy] = useState<string>('-created_at'); // Default sort: newest first
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [totalPackages, setTotalPackages] = useState<number>(0);

  const visaTypes = [
    { value: 'VISA_FREE', label: 'Visa Free' },
    { value: 'E_VISA', label: 'E-Visa' },
    { value: 'ON_ARRIVAL', label: 'On Arrival' },
    { value: 'STICKER_VISA', label: 'Sticker Visa' },
  ];
  const [selectedVisaType, setSelectedVisaType] = useState<string>('');


  const fetchPackages = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params: Record<string, any> = { page: currentPage, ordering: sortBy };
      if (selectedCountry) params['country__id'] = selectedCountry;
      if (selectedVisaType) params['visa_type'] = selectedVisaType;
      if (searchTerm) params['search'] = searchTerm;

      const data: PaginatedResponse<TourPackage> = await getTourPackages(params);
      setPackages(data.results);
      setTotalPackages(data.count);
      // Assuming PAGE_SIZE is 10 (as set in DRF settings)
      setTotalPages(Math.ceil(data.count / 10));
    } catch (err) {
      setError('Failed to fetch tour packages.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [currentPage, selectedCountry, selectedVisaType, searchTerm, sortBy]);

  useEffect(() => {
    fetchPackages();
  }, [fetchPackages]);

  useEffect(() => {
    const fetchFilterData = async () => {
      try {
        // Fetch all countries for the filter dropdown (assuming not too many)
        // For large numbers, consider a searchable dropdown or paginated fetching for the filter itself
        const countryData = await getCountries({ page_size: 200 }); // Fetch up to 200 countries
        setCountries(countryData.results);
      } catch (err) {
        console.error("Failed to fetch countries for filters", err);
      }
    };
    fetchFilterData();
  }, []);

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
    setCurrentPage(1); // Reset to first page on new search
  };

  const handleCountryChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedCountry(event.target.value);
    setCurrentPage(1);
  };

  const handleVisaTypeChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedVisaType(event.target.value);
    setCurrentPage(1);
  };

  const handleSortChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSortBy(event.target.value);
    setCurrentPage(1);
  };

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
  };

  if (loading && packages.length === 0) return <p>Loading packages...</p>;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;

  return (
    <div>
      <h2>Tour Packages</h2>

      {/* Filters Section */}
      <div style={{ marginBottom: '20px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <input
          type="text"
          placeholder="Search packages..."
          value={searchTerm}
          onChange={handleSearchChange}
        />
        <select value={selectedCountry} onChange={handleCountryChange}>
          <option value="">All Countries</option>
          {countries.map(country => (
            <option key={country.id} value={country.id.toString()}>{country.name}</option>
          ))}
        </select>
        <select value={selectedVisaType} onChange={handleVisaTypeChange}>
          <option value="">All Visa Types</option>
          {visaTypes.map(vt => (
            <option key={vt.value} value={vt.value}>{vt.label}</option>
          ))}
        </select>
        <select value={sortBy} onChange={handleSortChange}>
          <option value="-created_at">Newest First</option>
          <option value="created_at">Oldest First</option>
          <option value="price">Price: Low to High</option>
          <option value="-price">Price: High to Low</option>
          <option value="title">Title (A-Z)</option>
          <option value="-title">Title (Z-A)</option>
        </select>
      </div>

      {loading && <p>Updating list...</p>}

      <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center' }}>
        {packages.length > 0 ? (
          packages.map(pkg => <PackageCard key={pkg.id} tourPackage={pkg} />)
        ) : (
          !loading && <p>No tour packages found matching your criteria.</p>
        )}
      </div>

      {/* Pagination Section */}
      {totalPages > 1 && (
        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          {Array.from({ length: totalPages }, (_, i) => i + 1).map(pageNumber => (
            <button
              key={pageNumber}
              onClick={() => handlePageChange(pageNumber)}
              disabled={currentPage === pageNumber}
              style={{ margin: '0 5px', fontWeight: currentPage === pageNumber ? 'bold' : 'normal' }}
            >
              {pageNumber}
            </button>
          ))}
          <p>Page {currentPage} of {totalPages} (Total: {totalPackages} packages)</p>
        </div>
      )}
    </div>
  );
};

export default TourPackagesListPage;
