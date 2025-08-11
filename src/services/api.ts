import axios from 'axios';
import type { User, Transaction, PaymentRequest, ApiResponse } from '@/types';

// Extend window interface for mock API
declare global {
  interface Window {
    __MOCK_API__?: { user: User; transactions: Transaction[] };
  }
}

// Configure axios instance with Django backend base URL
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API service class following clean architecture principles
export class FinanceApiService {
  // User authentication and profile
  static async getCurrentUser(): Promise<User> {
    // Use mock data if available (for development without backend)
    if (window.__MOCK_API__) {
      return Promise.resolve(window.__MOCK_API__.user);
    }
    
    const response = await api.get<ApiResponse<User>>('/users/profile');
    return response.data.data;
  }

  static async updateBalance(userId: number): Promise<User> {
    if (window.__MOCK_API__) {
      return Promise.resolve(window.__MOCK_API__.user);
    }
    const response = await api.get<ApiResponse<User>>(`/users/${userId}/balance`);
    return response.data.data;
  }

  // Transaction management
  static async getTransactions(
    page: number = 1,
    limit: number = 10,
    filter?: string
  ): Promise<{ transactions: Transaction[]; total: number }> {
    // Use mock data if available (for development without backend)
    if (window.__MOCK_API__) {
      const allTransactions = window.__MOCK_API__.transactions;
      const startIndex = (page - 1) * limit;
      const endIndex = startIndex + limit;
      const paginatedTransactions = allTransactions.slice(startIndex, endIndex);
      
      return Promise.resolve({
        transactions: paginatedTransactions,
        total: allTransactions.length
      });
    }
    
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(filter && { filter }),
    });
    
    const response = await api.get<ApiResponse<{ transactions: Transaction[]; total: number }>>(
      `/transactions?${params}`
    );
    return response.data.data;
  }

  static async createTransaction(payment: PaymentRequest): Promise<Transaction> {
    if (window.__MOCK_API__) {
      // Create a mock transaction for development
      const mockTransaction: Transaction = {
        id: Date.now(),
        amount: payment.amount,
        description: payment.description,
        type: payment.amount > 0 ? 'credit' : 'debit',
        date: new Date().toISOString(),
        status: 'completed'
      };
      return Promise.resolve(mockTransaction);
    }
    
    const response = await api.post<ApiResponse<Transaction>>('/transactions', payment);
    return response.data.data;
  }

  static async getTransactionById(id: number): Promise<Transaction> {
    if (window.__MOCK_API__) {
      const transaction = window.__MOCK_API__.transactions.find(t => t.id === id);
      if (transaction) {
        return Promise.resolve(transaction);
      }
      throw new Error('Transaction not found');
    }
    
    const response = await api.get<ApiResponse<Transaction>>(`/transactions/${id}`);
    return response.data.data;
  }
}