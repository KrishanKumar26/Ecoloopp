'use client';

/**
 * Authentication Context Provider
 * Manages global authentication state across the application
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { loginUser, registerUser, getCurrentUser, type User, type LoginRequest, type RegisterRequest } from '@/lib/api';
import { saveToken, getToken, saveUser, getUser, clearAuth, isAuthenticated as checkAuth } from '@/lib/auth';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Load user from localStorage on mount
  useEffect(() => {
    const loadUser = async () => {
      const storedUser = getUser();
      const token = getToken();

      if (storedUser && token) {
        try {
          // Verify token is still valid by fetching current user
          const currentUser = await getCurrentUser(token);
          setUser(currentUser);
        } catch (error) {
          // Token is invalid or expired, clear auth
          console.error('Token validation failed:', error);
          clearAuth();
        }
      }

      setIsLoading(false);
    };

    loadUser();
  }, []);

  const login = async (credentials: LoginRequest) => {
    try {
      const response = await loginUser(credentials);

      // Save token and user data
      saveToken(response.access_token);
      saveUser(response.user);
      setUser(response.user);

      // Redirect to dashboard
      router.push('/');
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const register = async (data: RegisterRequest) => {
    try {
      const response = await registerUser(data);

      // After registration, automatically log in
      await login({ email: data.email, password: data.password });
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  };

  const logout = () => {
    clearAuth();
    setUser(null);
    router.push('/login');
  };

  const refreshUser = async () => {
    const token = getToken();
    if (token) {
      try {
        const currentUser = await getCurrentUser(token);
        setUser(currentUser);
        saveUser(currentUser);
      } catch (error) {
        console.error('Failed to refresh user:', error);
        // Token might be expired, logout
        logout();
      }
    }
  };

  const value = {
    user,
    isLoading,
    isAuthenticated: user !== null,
    login,
    register,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
