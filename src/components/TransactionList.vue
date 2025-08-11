<template>
  <div class="bg-white rounded-xl shadow-lg overflow-hidden">
    <div class="p-6 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-900">Recent Transactions</h3>
        <button
          @click="$emit('refresh')"
          class="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1"
        >
          <ArrowPathIcon class="h-4 w-4" />
          Refresh
        </button>
      </div>
    </div>

    <div class="divide-y divide-gray-200">
      <div v-if="loading" class="p-6 text-center text-gray-500">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-2">Loading transactions...</p>
      </div>

      <div v-else-if="transactions.length === 0" class="p-6 text-center text-gray-500">
        <p>No transactions found</p>
      </div>

      <div
        v-else
        v-for="transaction in transactions"
        :key="transaction.id"
        class="p-4 hover:bg-gray-50 transition-colors duration-150"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div
              :class="[
                'flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center',
                transaction.type === 'credit'
                  ? 'bg-green-100 text-green-600'
                  : 'bg-red-100 text-red-600'
              ]"
            >
              <ArrowUpIcon
                v-if="transaction.type === 'credit'"
                class="h-5 w-5 transform rotate-45"
              />
              <ArrowDownIcon
                v-else
                class="h-5 w-5 transform -rotate-45"
              />
            </div>
            <div>
              <p class="text-sm font-medium text-gray-900">
                {{ transaction.description }}
              </p>
              <p class="text-xs text-gray-500">
                {{ formatDate(transaction.timestamp) }} • {{ transaction.category }}
              </p>
              <div class="flex items-center mt-1">
                <span
                  :class="[
                    'inline-flex px-2 py-1 text-xs font-medium rounded-full',
                    getStatusColor(transaction.status)
                  ]"
                >
                  {{ transaction.status }}
                </span>
              </div>
            </div>
          </div>
          <div class="text-right">
            <p
              :class="[
                'text-sm font-semibold',
                transaction.type === 'credit' ? 'text-green-600' : 'text-red-600'
              ]"
            >
              {{ transaction.type === 'credit' ? '+' : '-' }}
              {{ formatCurrency(transaction.amount) }}
            </p>
            <p v-if="transaction.recipientAccount" class="text-xs text-gray-500">
              To: {{ transaction.recipientAccount }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="pagination.totalPages > 1" class="p-4 border-t border-gray-200">
      <div class="flex items-center justify-between">
        <button
          @click="$emit('changePage', pagination.currentPage - 1)"
          :disabled="pagination.currentPage === 1"
          class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        <span class="text-sm text-gray-700">
          Page {{ pagination.currentPage }} of {{ pagination.totalPages }}
        </span>
        <button
          @click="$emit('changePage', pagination.currentPage + 1)"
          :disabled="pagination.currentPage === pagination.totalPages"
          class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  ArrowPathIcon,
  ArrowUpIcon,
  ArrowDownIcon,
} from '@heroicons/vue/24/outline';
import type { Transaction } from '@/types';

interface Props {
  transactions: Transaction[];
  loading: boolean;
  pagination: {
    currentPage: number;
    totalPages: number;
    total: number;
    limit: number;
  };
}

interface Emits {
  (e: 'refresh'): void;
  (e: 'changePage', page: number): void;
}

defineProps<Props>();
defineEmits<Emits>();

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

const getStatusColor = (status: string): string => {
  const colors = {
    completed: 'bg-green-100 text-green-800',
    pending: 'bg-yellow-100 text-yellow-800',
    failed: 'bg-red-100 text-red-800',
  };
  return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
};
</script>