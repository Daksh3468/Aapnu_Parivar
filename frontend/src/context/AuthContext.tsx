import React, { createContext, useContext, useState } from 'react';

export interface UserProfile {
  user_id: string;
  login_id: string;
  role: string;
  status: string;
  person_id?: string;
  family_id?: string;
  is_head?: boolean;
}

export const isOfficerRole = (role?: string | null): boolean => {
  if (!role) return false;
  const upper = role.toUpperCase();
  return (
    upper.includes('OFFICER') ||
    upper.includes('ADMIN') ||
    ['STATE_ADMIN', 'DISTRICT_OFFICER', 'FIELD_OFFICER', 'OFFICER', 'ADMIN'].includes(upper)
  );
};

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  loginToken: (accessToken: string, refreshToken: string, profile: UserProfile) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));
  const [user, setUser] = useState<UserProfile | null>(() => {
    const saved = localStorage.getItem('user_profile');
    return saved ? JSON.parse(saved) : null;
  });

  const loginToken = (accessToken: string, refreshToken: string, profile: UserProfile) => {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
    localStorage.setItem('user_profile', JSON.stringify(profile));
    setToken(accessToken);
    setUser(profile);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_profile');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        loginToken,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
