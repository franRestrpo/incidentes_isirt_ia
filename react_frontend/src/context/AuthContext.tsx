import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import type { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthService } from '../services/authService';
import type { User, AuthState } from '../services/authService';

interface AuthContextType extends AuthState {
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const initializedRef = useRef(false);

  useEffect(() => {
    if (initializedRef.current) return;
    initializedRef.current = true;

    const initializeAuth = async () => {
      try {
        const user = await AuthService.checkSession();
        setCurrentUser(user);
      } catch (error) {
        console.error("Error initializing auth:", error);
        setCurrentUser(null);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (username: string, password: string) => {
    const user = await AuthService.login(username, password);
    setCurrentUser(user);
  };

  const logout = async () => {
    await AuthService.logout();
    setCurrentUser(null);
  };

  return (
    <AuthContext.Provider value={{
      currentUser,
      loading,
      login,
      logout,
      setUser: setCurrentUser
    }}>
      {children}
    </AuthContext.Provider>
  );
};

interface ProtectedRouteProps {
  children: ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { currentUser, loading } = useAuth();

  if (loading) {
    // Muestra un spinner o un componente de carga mientras se verifica la sesión.
    return <div className="flex min-h-screen items-center justify-center">Verificando sesión...</div>;
  }

  if (!currentUser) {
    // Si la carga ha terminado y no hay usuario, redirige al login.
    return <Navigate to="/login" replace />;
  }

  // Si la carga ha terminado y hay un usuario, muestra el contenido protegido.
  return <>{children}</>;
};