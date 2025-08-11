import { createApp } from 'vue';
import './style.css';
import App from './App.vue';

// Mock data for demonstration since Django backend isn't running
const mockUser = {
  id: 1,
  email: 'john.doe@example.com',
  firstName: 'John',
  lastName: 'Doe',
  balance: 12450.75,
  accountNumber: '****1234',
};

const mockTransactions = [
  {
    id: 1,
    amount: 250.00,
    type: 'credit' as const,
    description: 'Salary Deposit',
    category: 'income',
    timestamp: new Date(Date.now() - 86400000).toISOString(),
    status: 'completed' as const,
  },
  {
    id: 2,
    amount: 89.99,
    type: 'debit' as const,
    description: 'Online Shopping',
    category: 'shopping',
    recipientAccount: 'AMZ****8901',
    timestamp: new Date(Date.now() - 172800000).toISOString(),
    status: 'completed' as const,
  },
  {
    id: 3,
    amount: 1200.00,
    type: 'debit' as const,
    description: 'Rent Payment',
    category: 'bills',
    recipientAccount: 'PROP****5678',
    timestamp: new Date(Date.now() - 259200000).toISOString(),
    status: 'completed' as const,
  },
];

// Mock API responses for development
window.__MOCK_API__ = {
  user: mockUser,
  transactions: mockTransactions,
};

createApp(App).mount('#app');