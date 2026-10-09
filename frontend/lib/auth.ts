/**
 * Authentication utilities for client-side token management
 *
 * Security Note: We use localStorage for JWT storage in this demo.
 * For production, consider:
 * 1. HttpOnly cookies (requires backend cookie management)
 * 2. Session tokens with refresh mechanism
 * 3. Short token expiry times (30 minutes)
 *
 * Trade-off: localStorage is vulnerable to XSS but provides simpler
 * implementation for demo purposes. Ensure proper input sanitization
 * and CSP headers are in place.
 */

const TOKEN_KEY = 'ecoloop_access_token';
const USER_KEY = 'ecoloop_user';

export interface StoredUser {
  user_id: string;
  name: string;
  email: string;
  phone: string | null;
  role: string;
  eco_points: number;
  created_at: string;
}

/**
 * Save authentication token to localStorage
 */
export function saveToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_KEY, token);
  }
}

/**
 * Get authentication token from localStorage
 */
export function getToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(TOKEN_KEY);
  }
  return null;
}

/**
 * Remove authentication token from localStorage
 */
export function removeToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY);
  }
}

/**
 * Save user data to localStorage
 */
export function saveUser(user: StoredUser): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }
}

/**
 * Get user data from localStorage
 */
export function getUser(): StoredUser | null {
  if (typeof window !== 'undefined') {
    const userData = localStorage.getItem(USER_KEY);
    return userData ? JSON.parse(userData) : null;
  }
  return null;
}

/**
 * Remove user data from localStorage
 */
export function removeUser(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(USER_KEY);
  }
}

/**
 * Clear all authentication data (logout)
 */
export function clearAuth(): void {
  removeToken();
  removeUser();
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return getToken() !== null;
}
