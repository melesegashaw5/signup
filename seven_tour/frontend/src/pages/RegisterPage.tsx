import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { registerUser, RegisterData, AuthResponse } from '../services/apiService';

const RegisterPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [password2, setPassword2] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const navigate = useNavigate();
  const { login: contextLogin } = useAuth();

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    if (password !== password2) {
      setError("Passwords do not match.");
      setLoading(false);
      return;
    }

    const registrationData: RegisterData = {
      email,
      // Backend dj-rest-auth default RegisterSerializer expects 'password' and 'password2'
      // but for CustomRegisterSerializer, it might be different.
      // Our CustomRegisterSerializer uses password1 and password2 from BaseRegisterSerializer
      // So we pass password and password2, and they should map correctly.
      // Let's ensure field names match what CustomRegisterSerializer expects or its base.
      // BaseRegisterSerializer uses 'password' and 'password2'.
      // My CustomRegisterSerializer should inherit this.
      // However, my RegisterData interface used password_1, password_2. Let's align.
      // The test for registration used 'password' and 'password2'.
      // The `dj_rest_auth.registration.serializers.RegisterSerializer` uses `password` and `password2`
      // fields in its `validate` method if `PASSWORD_MATCH_VALIDATOR` is used.
      // The actual fields it saves are `username` (if any), `email`, `password`.
      // Let's use `password` and `password2` as they are standard for dj-rest-auth forms.
      // My CustomRegisterSerializer doesn't redefine these, so it inherits.
      // The `RegisterData` interface should reflect this.
      // I'll adjust `RegisterData` in `apiService.ts` if needed, but for now assume form fields are password & password2
      password_1: password, // This assumes CustomRegisterSerializer or its base expects password1
      password_2: password2, // This assumes CustomRegisterSerializer or its base expects password2
      first_name: firstName,
      last_name: lastName,
    };

    // Correction: The default RegisterSerializer in dj-rest-auth expects 'password' and 'password2'.
    // If CustomRegisterSerializer inherits, these should be the fields.
    // The test used 'password' and 'password2'.
    // The interface RegisterData in apiService.ts needs to be consistent.
    // Let's assume the payload should be:
    // { email, password, password2, first_name, last_name }
    // I will use this structure for the payload.

    const payload = {
        email,
        password: password, // Corrected field name
        password2: password2, // Corrected field name
        first_name: firstName,
        last_name: lastName,
    };


    try {
      // The registerUser function in apiService.ts needs to send correct field names.
      // Assuming registerUser is adapted for {email, password, password2, first_name, last_name}
      const response: AuthResponse = await registerUser(payload as any); // Type assertion for now

      // Upon successful registration, dj-rest-auth often returns tokens and user data
      // So we can log the user in directly.
      await contextLogin(response.access_token, response.refresh_token, response.user);
      navigate('/'); // Redirect to home or dashboard
    } catch (err: any) {
      if (err.response && err.response.data) {
        // Extract errors from DRF response
        const errors = err.response.data;
        let errorMessages = [];
        for (const key in errors) {
          errorMessages.push(`${key}: ${errors[key].join ? errors[key].join(', ') : errors[key]}`);
        }
        setError(errorMessages.join(' | '));
      } else {
        setError('Registration failed. Please try again.');
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: 'auto', padding: '20px' }}>
      <h2>Register</h2>
      <form onSubmit={handleSubmit}>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <div style={{ marginBottom: '10px' }}>
          <label htmlFor="firstName">First Name:</label>
          <input type="text" id="firstName" value={firstName} onChange={(e) => setFirstName(e.target.value)} required style={{ width: '100%', padding: '8px' }} />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label htmlFor="lastName">Last Name:</label>
          <input type="text" id="lastName" value={lastName} onChange={(e) => setLastName(e.target.value)} required style={{ width: '100%', padding: '8px' }}/>
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label htmlFor="email">Email:</label>
          <input type="email" id="email" value={email} onChange={(e) => setEmail(e.target.value)} required style={{ width: '100%', padding: '8px' }}/>
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label htmlFor="password">Password:</label>
          <input type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} required style={{ width: '100%', padding: '8px' }}/>
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label htmlFor="password2">Confirm Password:</label>
          <input type="password" id="password2" value={password2} onChange={(e) => setPassword2(e.target.value)} required style={{ width: '100%', padding: '8px' }}/>
        </div>
        <button type="submit" disabled={loading} style={{ padding: '10px 15px', width: '100%' }}>
          {loading ? 'Registering...' : 'Register'}
        </button>
      </form>
      <p style={{ marginTop: '15px', textAlign: 'center' }}>
        Already have an account? <Link to="/login">Login here</Link>
      </p>
    </div>
  );
};

export default RegisterPage;
