import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { loginUser, LoginData, AuthResponse, loginWithGoogle } from '../services/apiService';
import { GoogleLogin, CredentialResponse } from '@react-oauth/google';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const navigate = useNavigate();
  const { login: contextLogin } = useAuth();

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    const loginData: LoginData = { email, password };

    try {
      const response: AuthResponse = await loginUser(loginData);
      // loginUser from apiService should return the AuthResponse structure
      // which includes access_token, refresh_token, and user object
      await contextLogin(response.access_token, response.refresh_token, response.user);
      navigate('/'); // Redirect to home or dashboard
    } catch (err: any) {
      if (err.response && err.response.data) {
        const errors = err.response.data;
        let errorMessages = [];
        // dj-rest-auth often returns {'non_field_errors': ['Unable to log in with provided credentials.']}
        if (errors.non_field_errors) {
          errorMessages.push(...errors.non_field_errors);
        } else {
          for (const key in errors) {
            errorMessages.push(`${key}: ${errors[key].join ? errors[key].join(', ') : errors[key]}`);
          }
        }
        setError(errorMessages.join(' | ') || 'Login failed. Please check your credentials.');
      } else {
        setError('Login failed. Please try again.');
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLoginSuccess = async (credentialResponse: CredentialResponse) => {
    setLoading(true);
    setError(null);
    console.log("Google CredentialResponse:", credentialResponse);
    try {
      if (credentialResponse.credential) { // This is the ID token
        const response = await loginWithGoogle({ id_token: credentialResponse.credential });
        await contextLogin(response.access_token, response.refresh_token, response.user);
        navigate('/'); // Redirect to home or dashboard
      } else {
        setError('Google login failed: No credential received.');
      }
    } catch (err: any) {
      console.error("Google login error:", err);
      setError(err.response?.data?.detail || 'Google login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLoginError = () => {
    console.error('Google Login Failed');
    setError('Google login failed. Please try again.');
  };

  return (
    <div style={{ maxWidth: '400px', margin: 'auto', padding: '20px' }}>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <div style={{ marginBottom: '10px' }}>
          <label htmlFor="email">Email:</label>
          <input type="email" id="email" value={email} onChange={(e) => setEmail(e.target.value)} required style={{ width: '100%', padding: '8px' }}/>
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label htmlFor="password">Password:</label>
          <input type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} required style={{ width: '100%', padding: '8px' }}/>
        </div>
        <button type="submit" disabled={loading} style={{ padding: '10px 15px', width: '100%' }}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      <p style={{ marginTop: '10px' }}>
        {/* Link to password reset page can be added later */}
        {/* <Link to="/password-reset">Forgot password?</Link> */}
      </p>
      <p style={{ marginTop: '15px', textAlign: 'center' }}>
        Don't have an account? <Link to="/register">Register here</Link>
      </p>
      {/* Placeholder for Google Sign-In button */}
      <div style={{marginTop: '20px', textAlign: 'center'}}>
        <p>OR</p>
        <GoogleLogin
          onSuccess={handleGoogleLoginSuccess}
          onError={handleGoogleLoginError}
          useOneTap // Optional: use one-tap login experience
          shape="rectangular" // "rectangular", "pill", "circle", "square"
          theme="outline" // "outline", "filled_blue", "filled_black"
          size="large" // "small", "medium", "large"
          width="356px" // Example width, adjust as needed
        />
      </div>
    </div>
  );
};

export default LoginPage;
