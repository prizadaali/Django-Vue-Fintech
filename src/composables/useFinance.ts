import { ref, reactive, computed } from 'vue';
import { FinanceApiService } from '@/services/api';
import type { User, Transaction, PaymentRequest } from '@/types';

// Composable for financial data management
export function useFinance() {
  const user = ref<User | null>(null);
  const transactions = ref<Transaction[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const pagination = reactive({
    currentPage: 1,
    totalPages: 1,
    total: 0,
    limit: 10,
  });

  // Computed properties
  const formattedBalance = computed(() => {
    return user.value?.balance 
      ? new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
        }).format(user.value.balance)
      : '$0.00';
  });

  const recentTransactions = computed(() => {
    return transactions.value.slice(0, 5);
  });

  // Methods
  const fetchUser = async () => {
    try {
      loading.value = true;
      error.value = null;
      user.value = await FinanceApiService.getCurrentUser();
    } catch (err) {
      error.value = 'Failed to fetch user data';
      console.error('Error fetching user:', err);
    } finally {
      loading.value = false;
    }
  };

  const fetchTransactions = async (page: number = 1, filter?: string) => {
    try {
      loading.value = true;
      error.value = null;
      
      const result = await FinanceApiService.getTransactions(
        page,
        pagination.limit,
        filter
      );
      
      transactions.value = result.transactions;
      pagination.currentPage = page;
      pagination.total = result.total;
      pagination.totalPages = Math.ceil(result.total / pagination.limit);
    } catch (err) {
      error.value = 'Failed to fetch transactions';
      console.error('Error fetching transactions:', err);
    } finally {
      loading.value = false;
    }
  };

  const createPayment = async (payment: PaymentRequest): Promise<Transaction | null> => {
    try {
      loading.value = true;
      error.value = null;
      
      const newTransaction = await FinanceApiService.createTransaction(payment);
      
      // Update local state
      transactions.value.unshift(newTransaction);
      
      // Refresh user balance
      if (user.value) {
        user.value = await FinanceApiService.updateBalance(user.value.id);
      }
      
      return newTransaction;
    } catch (err) {
      error.value = 'Payment failed. Please try again.';
      console.error('Error creating payment:', err);
      return null;
    } finally {
      loading.value = false;
    }
  };

  const refreshData = async () => {
    await Promise.all([
      fetchUser(),
      fetchTransactions(pagination.currentPage),
    ]);
  };

  return {
    // State
    user,
    transactions,
    loading,
    error,
    pagination,
    
    // Computed
    formattedBalance,
    recentTransactions,
    
    // Methods
    fetchUser,
    fetchTransactions,
    createPayment,
    refreshData,
  };
}