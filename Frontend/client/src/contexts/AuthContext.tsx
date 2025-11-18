import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * DUMMY AUTH CONTEXT FOR TESTING
 * 
 * This is a mock implementation that doesn't call any backend.
 * Use this while your backend is loading.
 * 
 * To switch back to real auth:
 * 1. Import api from '@/lib/api'
 * 2. Call api.getUserProfile() on mount
 * 3. Call api.logout() on logout
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Simulate checking for existing session
  useEffect(() => {
    setTimeout(() => {
      // Check if user is stored in localStorage (from previous dummy login)
      const storedUser = localStorage.getItem('dummyUser');
      if (storedUser) {
        try {
          setUser(JSON.parse(storedUser));
        } catch (e) {
          console.error('Failed to parse stored user');
        }
      }
      setIsLoading(false);
    }, 500); // Simulate network delay
  }, []);

  /**
   * Dummy login - accepts any credentials
   * Creates a fake user object
   */
  const login = async (email: string, password: string) => {
    // Simulate network delay
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // Accept any email/password combination for testing
    const dummyUser: User = {
      id: Math.floor(Math.random() * 10000), // Random ID
      email,
      first_name: email.split('@')[0], // Use part of email as first name
      last_name: 'Demo User',
      role: email.includes('admin') ? 'admin' : 'insurer', // admin if email contains "admin"
    };

    setUser(dummyUser);
    localStorage.setItem('dummyUser', JSON.stringify(dummyUser));
  };

  /**
   * Dummy logout - just clear state
   */
  const logout = () => {
    setUser(null);
    localStorage.removeItem('dummyUser');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        setUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
