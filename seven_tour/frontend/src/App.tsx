import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import './App.css'; // You might want to create this file for App specific styles

import TourPackagesListPage from './pages/TourPackagesListPage';
import TourPackageDetailPage from './pages/TourPackageDetailPage';
import PrivacyPolicyPage from './pages/PrivacyPolicyPage';
import TermsOfServicePage from './pages/TermsOfServicePage';
import CookiePolicyPage from './pages/CookiePolicyPage';
import RegisterPage from './pages/RegisterPage';
import LoginPage from './pages/LoginPage';
import { useAuth } from './contexts/AuthContext'; // To conditionally show links

function Home() {
  const { isAuthenticated, user } = useAuth();
  return (
    <div>
      <h2>Home - Welcome to Seven Tour Operator</h2>
      {isAuthenticated && user ? <p>Welcome back, {user.first_name || user.email}!</p> : <p>Your gateway to amazing travel experiences in Ethiopia and beyond.</p>}
      <Link to="/packages">Browse Tour Packages</Link>
    </div>
  );
}

// Basic Profile Page Placeholder
const ProfilePage: React.FC = () => {
  const { user, logout, isLoading } = useAuth();
  const navigate = useNavigate();

  if (isLoading) return <p>Loading profile...</p>;
  if (!user) {
    // This shouldn't happen if route is protected, but good fallback
    navigate('/login');
    return null;
  }

  const handleLogout = () => {
    logout();
    navigate('/'); // Redirect to home after logout
  };

  return (
    <div>
      <h2>User Profile</h2>
      <p><strong>Email:</strong> {user.email}</p>
      <p><strong>First Name:</strong> {user.first_name || 'N/A'}</p>
      <p><strong>Last Name:</strong> {user.last_name || 'N/A'}</p>
      <p><strong>Role:</strong> {user.role || 'N/A'}</p>
      <p><strong>Referral Code:</strong> {user.referral_code || 'N/A'}</p>
      {user.profile_photo_url ?
        <img src={user.profile_photo_url} alt="Profile" style={{width: '150px', height: '150px', borderRadius: '50%', objectFit: 'cover', margin: '10px 0'}}/> :
        <div style={{width: '150px', height: '150px', borderRadius: '50%', background: '#ccc', display: 'flex', justifyContent: 'center', alignItems: 'center', margin: '10px 0'}}>No Photo</div>
      }
      {/* TODO: Add forms/modals for profile update, photo upload, password change */}
      <div style={{marginTop: '10px'}}>
        <button onClick={() => alert("Profile update UI not implemented yet.")}>Edit Profile</button>
        <button onClick={() => alert("Password change UI not implemented yet.")} style={{marginLeft: '10px'}}>Change Password</button>
      </div>
      <button onClick={handleLogout} style={{ marginTop: '20px', background: 'red', color: 'white' }}>Logout</button>
    </div>
  );
}

// ProtectedRoute component (basic example)
const ProtectedRoute: React.FC<{ children: JSX.Element }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <div>Loading authentication state...</div>; // Or a spinner
  }

  if (!isAuthenticated) {
    // Redirect them to the /login page, but save the current location they were
    // trying to go to when they were redirected. This allows us to send them
    // along to that page after they login, which is a nicer user experience
    // than dropping them off on the home page.
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};


function App() {
  const { isAuthenticated, logout, user, isLoading } = useAuth(); // Get auth state
  const navigate = useNavigate(); // For logout redirect in nav

  const handleLogoutInNav = () => {
    logout();
    navigate('/');
  };

  return (
    <Router>
      <div>
        <nav style={{ padding: '10px', background: '#f0f0f0', marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <ul style={{ listStyleType: 'none', padding: 0, margin: 0, display: 'flex', gap: '20px' }}>
            <li>
              <Link to="/">Home</Link>
            </li>
            <li>
              <Link to="/packages">Packages</Link>
            </li>
          </ul>
          <ul style={{ listStyleType: 'none', padding: 0, margin: 0, display: 'flex', gap: '20px', alignItems: 'center' }}>
            {isLoading ? (
              <li>Loading...</li>
            ) : isAuthenticated && user ? (
              <>
                <li><Link to="/profile">{user.first_name || user.email}</Link></li>
                <li><button onClick={handleLogoutInNav} style={{background: 'none', border: 'none', color: 'blue', textDecoration: 'underline', cursor: 'pointer'}}>Logout</button></li>
              </>
            ) : (
              <>
                <li><Link to="/login">Login</Link></li>
                <li><Link to="/register">Register</Link></li>
              </>
            )}
          </ul>
        </nav>

        <div style={{ padding: '0 20px' }}> {/* Basic padding for content area */}
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/packages" element={<TourPackagesListPage />} />
            <Route path="/packages/:id" element={<TourPackageDetailPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/profile" element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            } />
            <Route path="/privacy-policy" element={<PrivacyPolicyPage />} />
            <Route path="/terms-of-service" element={<TermsOfServicePage />} />
            <Route path="/cookie-policy" element={<CookiePolicyPage />} />
            {/* More routes will be added here */}
          </Routes>
        </div>

        <footer style={{ textAlign: 'center', marginTop: '40px', padding: '20px', background: '#f0f0f0' }}>
          <ul style={{ listStyleType: 'none', padding: 0, margin: 0, display: 'flex', justifyContent: 'center', gap: '15px' }}>
            <li><Link to="/privacy-policy">Privacy Policy</Link></li>
            <li><Link to="/terms-of-service">Terms of Service</Link></li>
            <li><Link to="/cookie-policy">Cookie Policy</Link></li>
          </ul>
          <p style={{ marginTop: '10px' }}>© {new Date().getFullYear()} Seven Tour Operator. All rights reserved.</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
