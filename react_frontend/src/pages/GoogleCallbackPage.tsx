import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { AuthService } from '../services/authService';
import { useAuth } from '../context/AuthContext';

const GoogleCallbackPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const { setUser } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [, setLoading] = useState(true);

  useEffect(() => {
    const handleGoogleCallback = async () => {
      try {
        const code = searchParams.get('code');
        const errorParam = searchParams.get('error');

        // Verificar si hay error en los parámetros de URL
        if (errorParam) {
          throw new Error(`Error de Google OAuth: ${errorParam}`);
        }

        if (!code) {
          throw new Error('No se encontró el código de autorización de Google.');
        }

        // Validar que estamos en un contexto seguro
        if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost') {
          throw new Error('La autenticación OAuth requiere HTTPS en producción.');
        }

        // Construir redirect URI segura
        const redirectUri = `${window.location.origin}${window.location.pathname}`;

        // Procesar el callback usando el servicio
        const user = await AuthService.handleGoogleCallback(code, redirectUri);

        // Actualizar el estado de autenticación
        setUser(user);

        // Redirigir al dashboard
        window.location.href = `${window.location.origin}/dashboard`;

      } catch (err: any) {
        console.error('Google OAuth callback error:', err);

        // Handle specific case where user has password and tries Google login
        if (err.message && err.message.includes('Este usuario debe iniciar sesión con email y contraseña')) {
          // Redirect to login with specific message
          window.location.href = '/login?google_error=password_required';
          return;
        }

        setError(err.message || 'Ocurrió un error durante la autenticación.');
        setLoading(false);
      }
    };

    handleGoogleCallback();
  }, [searchParams, setUser]);

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold text-red-600 mb-4">
            Error de Autenticación
          </h2>
          <p className="text-gray-700 mb-4">{error}</p>
          <button
            onClick={() => window.location.href = '/login'}
            className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 transition-colors"
          >
            Volver al Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p className="text-gray-600">Finalizando autenticación...</p>
      </div>
    </div>
  );
};

export default GoogleCallbackPage;
