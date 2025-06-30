import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import apiClient from '../services/apiService'; // Assuming your API client is set up for JWTs

// Define the shape of the user object and auth state
interface User {
  pk: number; // or id, depending on your UserDetailsSerializer
  email: string;
  first_name?: string;
  last_name?: string;
  role?: string;
  profile_photo_url?: string | null;
  referral_code?: string;
  // Add other fields from your UserDetailsSerializer
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  isLoading: boolean; // To handle initial loading of user state
  login: (accessToken: string, refreshToken?: string, userData?: User) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<User | null>; // Function to fetch user details
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true); // Start loading initially

  useEffect(() => {
    const initializeAuth = async () => {
      const accessToken = localStorage.getItem('accessToken');
      if (accessToken) {
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
        try {
          // Fetch user details if token exists to validate it and get user info
          // This assumes your UserDetailsView is at '/auth/user/' (dj-rest-auth default)
          const response = await apiClient.get<User>('auth/user/');
          setUser(response.data);
          setIsAuthenticated(true);
        } catch (error) {
          console.error('Failed to fetch user with stored token, logging out:', error);
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          apiClient.defaults.headers.common['Authorization'] = '';
          setIsAuthenticated(false);
          setUser(null);
        }
      }
      setIsLoading(false);
    };
    initializeAuth();
  }, []);

  const login = async (accessToken: string, refreshToken?: string, userData?: User) => {
    localStorage.setItem('accessToken', accessToken);
    if (refreshToken) {
      localStorage.setItem('refreshToken', refreshToken);
    }
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
    if (userData) {
        setUser(userData);
    } else {
        // If userData is not passed during login (e.g. token obtained externally), fetch it
        await fetchUser();
    }
    setIsAuthenticated(true);
  };

  const logout = () => {
    // Call the backend logout endpoint if it does token blacklisting
    // apiClient.post('auth/logout/').catch(err => console.error("Logout API call failed", err));

    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    apiClient.defaults.headers.common['Authorization'] = '';
    setUser(null);
    setIsAuthenticated(false);
    // Optionally redirect to home or login page via useNavigate() if called from a component
  };

  const fetchUser = async (): Promise<User | null> => {
    setIsLoading(true);
    try {
      const response = await apiClient.get<User>('auth/user/');
      setUser(response.data);
      setIsAuthenticated(true); // Ensure authenticated state is true if user is fetched
      setIsLoading(false);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch user:', error);
      // Potentially logout if user fetch fails and an access token was present
      // logout();
      setIsLoading(false);
      return null;
    }
  };


  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, isLoading, fetchUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
