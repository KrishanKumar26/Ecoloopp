/**
 * API client for EcoLoop backend
 * Handles authentication, request/response formatting, and error handling
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export interface User {
  user_id: string;
  name: string;
  email: string;
  phone: string | null;
  role: string;
  eco_points: number;
  created_at: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  phone?: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ApiError {
  detail: string;
}

export interface ClassificationResult {
  classification_id: string;
  item_name: string;
  category: string;
  confidence: number;
  estimated_weight_kg: number;
  safety_tips: string[];
  special_care_warning: string | null;
  image_url: string | null;
  classified_at: string;
}

export interface ClassifyRequest {
  item_name: string;
  image?: File;
}

export interface Category {
  name: string;
  description: string;
  examples: string[];
}

export interface PickupAddress {
  street: string;
  city: string;
  state: string;
  pincode: string;
  lat: number;
  lng: number;
}

export interface CreatePickupRequest {
  classification_id?: string;
  item_description: string;
  estimated_weight_kg?: number;
  scheduled_at: string;  // ISO date string
  address: PickupAddress;
  notes?: string;
}

export interface Pickup {
  pickup_id: string;
  classification_id: string | null;
  item_description: string;
  scheduled_at: string;
  address: PickupAddress;
  status: string;
  otp: string | null;
  otp_expires_at: string | null;
  cancellation_reason: string | null;
  eco_points_awarded: boolean;
  created_at: string;
  updated_at: string;
}

export interface EcoPointTransaction {
  transaction_id: string;
  pickup_id: string | null;
  points: number;
  reason: string;
  created_at: string;
}

/**
 * Register a new user account
 */
export async function registerUser(data: RegisterRequest): Promise<{ user: User }> {
  const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || 'Registration failed');
  }

  return response.json();
}

/**
 * Login with email and password
 */
export async function loginUser(data: LoginRequest): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  return response.json();
}

/**
 * Get current authenticated user
 */
export async function getCurrentUser(token: string): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || 'Failed to get user');
  }

  return response.json();
}

/**
 * Classify an e-waste item
 */
export async function classifyItem(token: string, data: ClassifyRequest): Promise<ClassificationResult> {
  const formData = new FormData();
  formData.append('item_name', data.item_name);

  if (data.image) {
    formData.append('image', data.image);
  }

  const response = await fetch(`${API_BASE_URL}/api/classify`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || 'Classification failed');
  }

  return response.json();
}

/**
 * Get available e-waste categories
 */
export async function getCategories(token: string): Promise<{ categories: Category[] }> {
  const response = await fetch(`${API_BASE_URL}/api/classify/categories`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || 'Failed to get categories');
  }

  return response.json();
}

/**
 * Get user's classification history
 */
export async function getClassificationHistory(token: string): Promise<{ classifications: ClassificationResult[] }> {
  const response = await fetch(`${API_BASE_URL}/api/classify/history`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || 'Failed to get classification history');
  }

  return response.json();
}

/**
 * Create a new pickup request
 */
export async function createPickup(token: string, data: CreatePickupRequest): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/pickups`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || 'Failed to create pickup');
  }

  return response.json();
}

/**
 * Get user's pickups
 */
export async function getPickups(token: string, statusFilter?: string): Promise<{ pickups: Pickup[], total: number }> {
  const url = new URL(`${API_BASE_URL}/api/pickups`);
  if (statusFilter) {
    url.searchParams.append('status_filter', statusFilter);
  }

  const response = await fetch(url.toString(), {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || 'Failed to get pickups');
  }

  return response.json();
}

/**
 * Get pickup details
 */
export async function getPickup(token: string, pickupId: string): Promise<Pickup> {
  const response = await fetch(`${API_BASE_URL}/api/pickups/${pickupId}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || 'Failed to get pickup');
  }

  return response.json();
}

/**
 * Cancel a pickup
 */
export async function cancelPickup(token: string, pickupId: string, reason: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/pickups/${pickupId}/cancel`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ reason }),
  });

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || 'Failed to cancel pickup');
  }

  return response.json();
}

/**
 * Complete a pickup with OTP
 */
export async function completePickup(token: string, pickupId: string, otp: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/pickups/${pickupId}/complete`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ otp }),
  });

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || 'Failed to complete pickup');
  }

  return response.json();
}

/**
 * Get EcoPoints balance
 */
export async function getEcoPointsBalance(token: string): Promise<{ user_id: string, balance: number, name: string }> {
  const response = await fetch(`${API_BASE_URL}/api/ecopoints/balance`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || 'Failed to get EcoPoints balance');
  }

  return response.json();
}

/**
 * Get EcoPoints transaction history
 */
export async function getEcoPointsTransactions(token: string, limit = 50): Promise<{ transactions: EcoPointTransaction[], total: number, current_balance: number }> {
  const response = await fetch(`${API_BASE_URL}/api/ecopoints/transactions?limit=${limit}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || 'Failed to get transactions');
  }

  return response.json();
}

/**
 * Get EcoPoints statistics
 */
export async function getEcoPointsStats(token: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/ecopoints/stats`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || 'Failed to get stats');
  }

  return response.json();
}
