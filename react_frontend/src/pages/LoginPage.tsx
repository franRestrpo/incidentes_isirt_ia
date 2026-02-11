import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { AuthService } from '../services/authService';
import { Card, TextInput, Button, Text } from '@tremor/react';

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const googleError = searchParams.get('google_error');
    if (googleError === 'password_required') {
      setError('Esta cuenta requiere inicio de sesión con email y contraseña. Por favor use sus credenciales de email.');
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validación básica del frontend
    if (!username.trim() || !password.trim()) {
      setError('Por favor ingrese email y contraseña.');
      setLoading(false);
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(username)) {
      setError('Por favor ingrese un email válido.');
      setLoading(false);
      return;
    }

    try {
      await login(username, password);
      navigate('/dashboard');
    } catch (err: any) {
      // Mejorar el manejo de errores
      const errorMessage = err.message || 'Ocurrió un error inesperado.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    // Usar el servicio para obtener la URL segura
    window.location.href = AuthService.getGoogleLoginUrl();
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-50 p-4">
      <div className="w-full max-w-sm">
        <Card className="p-6">
          <h2 className="text-2xl font-bold text-center text-slate-800 mb-6">Iniciar Sesión</h2>
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && <Text className="text-red-500 text-center">{error}</Text>}
            <div className="space-y-2">
              <label htmlFor="username" className="text-sm font-medium text-slate-600">Correo Electrónico</label>
              <TextInput
                type="email"
                id="username"
                value={username}
                onValueChange={setUsername}
                required
                placeholder="usuario@ejemplo.com"
                disabled={loading}
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium text-slate-600">Contraseña</label>
              <TextInput
                type="password"
                id="password"
                value={password}
                onValueChange={setPassword}
                required
                placeholder="Ingrese su contraseña"
                disabled={loading}
              />
            </div>
            <Button 
              type="submit" 
              className="w-full" 
              loading={loading}
              disabled={loading}
            >
              Ingresar
            </Button>
          </form>

          <div className="mt-6 flex items-center">
            <div className="flex-grow border-t border-slate-300"></div>
            <span className="mx-4 text-sm text-slate-500">O</span>
            <div className="flex-grow border-t border-slate-300"></div>
          </div>

          <div className="mt-6">
            <Button
              variant="secondary"
              className="w-full flex items-center justify-center"
              disabled={loading}
              onClick={handleGoogleLogin}
            >
              {/* TODO: Add Google Icon */}
              <span className="ml-2">Continuar con Google</span>
            </Button>
          </div>

        </Card>
      </div>
    </div>
  );
};

export default LoginPage;