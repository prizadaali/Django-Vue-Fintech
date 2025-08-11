// Type definitions for the fintech application
export interface User {
  id: number;
  email: string;
  firstName: string;
  lastName: string;
  balance: number;
  accountNumber: string;
}

export interface Transaction {
  id: number;
  amount: number;
  type: 'credit' | 'debit';
  description: string;
  category: string;
  recipientAccount?: string;
  timestamp: string;
  status: 'pending' | 'completed' | 'failed';
}

export interface PaymentRequest {
  amount: number;
  recipientAccount: string;
  description: string;
  category: string;
}

export interface ApiResponse<T> {
  data: T;
  message: string;
  success: boolean;
}