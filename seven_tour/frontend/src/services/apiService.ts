import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1/';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Define interfaces for our data models (can be expanded)
export interface Country {
  id: number;
  name: string;
  country_code: string | null;
}

export interface Destination {
  id: number;
  name: string;
  description: string | null;
  country_id: number;
  country_name: string;
}

export interface TourPackage {
  id: number;
  title: string;
  description: string;
  country: Country | null; // Assuming nested serializer for GET
  destinations: Destination[]; // Assuming nested serializer for GET
  visa_type: string;
  visa_type_display: string;
  price: string; // Decimal fields often come as strings
  highlights: string;
  inclusions: string;
  exclusions: string;
  duration_days: number | null;
  main_image: string | null; // URL to the image
  is_active: boolean;
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// API functions
export const getTourPackages = async (params: Record<string, any> = {}): Promise<PaginatedResponse<TourPackage>> => {
  const response = await apiClient.get<PaginatedResponse<TourPackage>>('tours/packages/', { params });
  return response.data;
};

export const getTourPackageById = async (id: number): Promise<TourPackage> => {
  const response = await apiClient.get<TourPackage>(`tours/packages/${id}/`);
  return response.data;
};

export const getCountries = async (params: Record<string, any> = {}): Promise<PaginatedResponse<Country>> => {
  const response = await apiClient.get<PaginatedResponse<Country>>('tours/countries/', { params });
  return response.data;
};

export const getDestinations = async (params: Record<string, any> = {}): Promise<PaginatedResponse<Destination>> => {
  const response = await apiClient.get<PaginatedResponse<Destination>>('tours/destinations/', { params });
  return response.data;
};

// Auth types (can be expanded)
export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: User; // Assuming User interface is defined above or imported
}

export interface RegisterData {
  email: string;
  password?: string; // Made optional to align with typical form handling where it's confirmed by password2
  password2?: string; // For password confirmation. dj-rest-auth default RegisterSerializer uses this.
  first_name?: string;
  last_name?: string;
  // Ensure these field names match what your CustomRegisterSerializer expects as input.
  // The BaseRegisterSerializer expects 'email', 'password', 'password2'.
  // Our CustomRegisterSerializer adds 'first_name', 'last_name'.
}

export interface LoginData {
  email: string;
  password: string;
}


// Auth API functions
export const registerUser = async (data: RegisterData): Promise<AuthResponse> => {
  // dj-rest-auth's default register serializer uses 'password1' and 'password2'
  // but our CustomRegisterSerializer might expect 'password' and 'password2' or just 'password'
  // if it inherits and overrides. Let's assume it aligns with 'password' and 'password2'
  // or the fields defined in CustomRegisterSerializer.
  // For now, matching common dj-rest-auth pattern.
  const payload = {
    ...data,
    // Ensure field names match what CustomRegisterSerializer expects.
    // If CustomRegisterSerializer expects 'password' and 'password2', adjust here.
    // The default RegisterSerializer in dj-rest-auth uses password, password2.
    // My CustomRegisterSerializer does not explicitly redefine these, so it should inherit.
  };
  // dj_rest_auth.registration.urls is typically mounted at 'auth/registration/'
  const response = await apiClient.post<AuthResponse>('auth/registration/', payload);
  return response.data;
};

export const loginUser = async (data: LoginData): Promise<AuthResponse> => {
  // dj_rest_auth.urls is typically mounted at 'auth/'
  const response = await apiClient.post<AuthResponse>('auth/login/', data);
  return response.data;
};

export const logoutUser = async (): Promise<void> => {
  // dj-rest-auth logout endpoint
  // This might not be strictly necessary if JWTs are just cleared client-side
  // but good practice if backend does token blacklisting.
  try {
    await apiClient.post('auth/logout/');
  } catch (error) {
    console.warn("Logout API call failed (might be okay if backend doesn't blacklist):", error);
    // Don't let this block client-side logout
  }
};

export const fetchUserDetails = async (): Promise<User> => {
  const response = await apiClient.get<User>('auth/user/');
  return response.data;
}

export interface GoogleLoginData {
  access_token?: string; // from Google
  id_token?: string; // from Google, often preferred by dj-rest-auth/allauth
}

export const loginWithGoogle = async (tokenData: GoogleLoginData): Promise<AuthResponse> => {
  // The backend endpoint /api/v1/auth/google/ is provided by dj-rest-auth for social login
  // It expects an access_token or id_token (or code, depending on backend allauth config)
  // For @react-oauth/google, we usually get an id_token (CredentialResponse.credential)
  // or an access_token (if using useGoogleLogin hook for explicit flow).
  // dj-rest-auth's SocialLoginView typically prefers 'access_token' or 'code'.
  // If using 'id_token', the backend SocialLoginView needs to be configured for it.
  // Let's assume for now we send 'id_token' as 'access_token' or the backend handles 'id_token'.
  // Common practice is to send the id_token as 'access_token' to dj-rest-auth's google endpoint,
  // or configure allauth to accept 'id_token' directly.
  // The default SocialLoginView in dj_rest_auth expects 'access_token' or 'code'.
  // If we get an id_token from Google, we might need to send it as 'id_token' and ensure
  // our backend SocialLoginView (if customized) or allauth setup handles it.
  // Or, send it as 'access_token' if allauth's Google provider is set up for that.

  // Simplest flow with @react-oauth/google's GoogleLogin component: it gives a credential (ID token).
  // Let's assume the backend /api/v1/auth/google/ can take 'id_token'.
  // If not, it needs to be configured or we send it as 'access_token'.
  // For dj-rest-auth, the `SocialLoginView` uses `allauth` which can use `id_token`.
  // The parameter name might need to be `id_token` or `access_token` depending on the specific
  // allauth provider adapter settings or if `dj_rest_auth.views.SocialLoginView` is customized.
  // The default Google provider in allauth can work with access_token.
  // If sending id_token, you might need to map it to 'access_token' or ensure backend accepts 'id_token'.

  // Let's assume we are sending the ID token as `id_token` and the backend is configured for it,
  // or we send it as `access_token` if that's what the dj-rest-auth endpoint expects.
  // The dj-rest-auth SocialLoginView for Google typically expects an 'access_token'.
  // The @react-oauth/google `GoogleLogin` onSuccess returns `credential` which is an ID token.
  // A common pattern is to send this ID token as `access_token` to the dj-rest-auth Google endpoint.

  const payload = tokenData.id_token ? { access_token: tokenData.id_token } : tokenData;

  const response = await apiClient.post<AuthResponse>('auth/google/', payload);
  return response.data;
};


// Add more functions as needed (e.g., for password reset, email verification, token refresh)

export default apiClient;

// Interceptor to handle token refresh if using JWTs and refresh tokens
// This is a more advanced setup. For now, we'll rely on access token expiry and re-login.
/*
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          // Make sure your backend has a token refresh endpoint
          const { data } = await apiClient.post('/auth/token/refresh/', { refresh: refreshToken });
          localStorage.setItem('accessToken', data.access);
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${data.access}`;
          originalRequest.headers['Authorization'] = `Bearer ${data.access}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Handle failed refresh (e.g., redirect to login)
        console.error('Token refresh failed:', refreshError);
        // Potentially call logout function from AuthContext here
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);
*/
