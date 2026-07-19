import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiClient } from '../services/api';
import { toast } from 'react-hot-toast';

interface UserProfile {
  email: string;
  full_name: string;
  avatar: string | null;
}

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, fullName: string, password: string, avatar: string) => Promise<void>;
  updateProfile: (profile: { full_name: string; avatar: string | null }) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const restoreSession = async () => {
      const storedToken = localStorage.getItem('token');
      if (!storedToken) {
        setIsLoading(false);
        return;
      }

      try {
        setToken(storedToken);
        const response = await apiClient.get('/auth/me');
        const profile = toUserProfile(response.data);
        localStorage.setItem('lh_user_profile', JSON.stringify(profile));
        setUser(profile);
      } catch (error) {
        localStorage.removeItem('token');
        localStorage.removeItem('lh_user_profile');
        setToken(null);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    restoreSession();
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await apiClient.post('/auth/login', { email, password });
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      setToken(access_token);

      const profileRes = await apiClient.get('/auth/me');
      const profile = toUserProfile(profileRes.data);
      localStorage.setItem('lh_user_profile', JSON.stringify(profile));
      setUser(profile);
      toast.success('Logged in successfully!');
    } catch (error: any) {
      const msg = error.response?.data?.detail || 'Failed to login.';
      toast.error(msg);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, fullName: string, password: string, avatar: string) => {
    setIsLoading(true);
    try {
      await apiClient.post('/auth/register', {
        email,
        full_name: fullName,
        password,
        avatar,
      });

      const loginRes = await apiClient.post('/auth/login', { email, password });
      const { access_token } = loginRes.data;
      localStorage.setItem('token', access_token);
      setToken(access_token);

      const profileRes = await apiClient.get('/auth/me');
      const profile = toUserProfile(profileRes.data);
      localStorage.setItem('lh_user_profile', JSON.stringify(profile));
      setUser(profile);
      toast.success('Account created and logged in!');
    } catch (error: any) {
      const msg = error.response?.data?.detail || 'Registration failed.';
      toast.error(msg);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const updateProfile = async (profile: { full_name: string; avatar: string | null }) => {
    setIsLoading(true);
    try {
      const response = await apiClient.put('/auth/me', profile);
      const updatedProfile = toUserProfile(response.data);
      localStorage.setItem('lh_user_profile', JSON.stringify(updatedProfile));
      setUser(updatedProfile);
      toast.success('Profile settings updated successfully!');
    } catch (error: any) {
      const msg = error.response?.data?.detail || 'Failed to update profile.';
      toast.error(msg);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('lh_user_profile');
    setToken(null);
    setUser(null);
    toast.success('Signed out.');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token,
        login,
        register,
        updateProfile,
        logout,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

function toUserProfile(data: any): UserProfile {
  return {
    email: data.email,
    full_name: data.full_name,
    avatar: data.avatar,
  };
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
