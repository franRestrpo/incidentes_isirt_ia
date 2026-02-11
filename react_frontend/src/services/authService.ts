/**
 * Servicio de autenticación
 *
 * Este servicio maneja toda la lógica de autenticación,
 * separando responsabilidades del contexto de React.
 */

import { apiService, isAuthError } from './apiService';

export interface User {
  id: number;
  username: string;
  role: string;
  is_active: boolean;
}

export interface AuthState {
  currentUser: User | null;
  loading: boolean;
}

export class AuthService {
  /**
   * Verifica la sesión actual del usuario
   */
  static async checkSession(): Promise<User | null> {
    try {
      const user = await apiService.getCurrentUser();
      if (!user) {
        return null;
      }
      return {
        id: user.user_id,
        username: user.email,
        role: user.role,
        is_active: user.is_active
      };
    } catch (error) {
      if (isAuthError(error)) {
        return null; // Silently handle auth errors, as it simply means no active session.
      }

      // For any other errors, log them, as they are unexpected during a session check.
      console.error("Unexpected error checking session:", error);
      return null;
    }
  }

  /**
   * Realiza login con email y contraseña
   */
  static async login(email: string, password: string): Promise<User> {
    await apiService.login(email, password);
    const user = await apiService.getCurrentUser();
    return {
      id: user.user_id,
      username: user.email,
      role: user.role,
      is_active: user.is_active
    };
  }

  /**
   * Realiza logout
   */
  static async logout(): Promise<void> {
    try {
      await apiService.logout();
    } catch (error) {
      console.error("Logout failed:", error);
      // No lanzamos error, el logout debe ser idempotente
    }
  }

  /**
   * Maneja el callback de Google OAuth
   */
  static async handleGoogleCallback(code: string, redirectUri: string): Promise<User> {
    // Validar parámetros
    if (!code || !redirectUri) {
      throw new Error('Código de autorización o URI de redirección faltante');
    }

    // Validar que el redirectUri sea seguro
    if (!this.isValidRedirectUri(redirectUri)) {
      throw new Error('URI de redirección no válida');
    }

    await apiService.exchangeGoogleCode(code, redirectUri);
    const user = await apiService.getCurrentUser();
    return {
      id: user.user_id,
      username: user.email,
      role: user.role,
      is_active: user.is_active
    };
  }

  /**
   * Valida que la URI de redirección sea segura
   */
  private static isValidRedirectUri(uri: string): boolean {
    try {
      const url = new URL(uri);
      const allowedOrigins = [
        window.location.origin,
        // Agregar otros orígenes permitidos si es necesario
      ];
      return allowedOrigins.includes(url.origin);
    } catch {
      return false;
    }
  }

  /**
   * Construye la URL de login de Google
   */
  static getGoogleLoginUrl(): string {
    return '/api/v1/login/google';
  }
}