<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <h1 class="text-2xl font-bold text-gray-900">FinTech Dashboard</h1>
          </div>
          <div v-if="user" class="flex items-center space-x-4">
            <span class="text-sm text-gray-700">{{ user.firstName }} {{ user.lastName }}</span>
            <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <span class="text-white text-sm font-medium">
                {{ user.firstName.charAt(0) }}{{ user.lastName.charAt(0) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Error Alert -->
      <div
        v-if="error"
        class="bg-red-50 border border-red-200 rounded-md p-4 mb-6"
      >
        <div class="flex">
          <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
          <div class="ml-3">
            <p class="text-sm text-red-800">{{ error }}</p>
          </div>
        </div>
      </div>

      <!-- Dashboard Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Balance Card -->
        <div class="lg:col-span-2">
          <BalanceCard
            :user="user"
            :formattedBalance="formattedBalance"
          />
        </div>

        <!-- Quick Stats -->
        <div class="space-y-4">
          <div class="bg-white p-4 rounded-lg shadow-sm">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <ArrowUpIcon class="h-5 w-5 text-green-500" />
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-900">This Month</p>
                <p class="text-xs text-gray-500">+$2,340.00</p>
              </div>
            </div>
          </div>
          <div class="bg-white p-4 rounded-lg shadow-sm">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <ArrowDownIcon class="h-5 w-5 text-red-500" />
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-900">Spent</p>
                <p class="text-xs text-gray-500">-$1,240.00</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Transaction List -->
        <div class="lg:col-span-2">
          <TransactionList
            :transactions="recentTransactions"
            :loading="loading"
            :pagination="pagination"
            @refresh="refreshData"
            @changePage="handlePageChange"
          />
        </div>

        <!-- Payment Form -->
        <div>
          <PaymentForm
            :loading="loading"
            @submit="handlePayment"
          />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import {
  ExclamationTriangleIcon,
  ArrowUpIcon,
  ArrowDownIcon,
} from '@heroicons/vue/24/outline';

import { useFinance } from '@/composables/useFinance';
import BalanceCard from '@/components/BalanceCard.vue';
import TransactionList from '@/components/TransactionList.vue';
import PaymentForm from '@/components/PaymentForm.vue';
import type { PaymentRequest } from '@/types';

const {
  user,
  transactions,
  loading,
  error,
  pagination,
  formattedBalance,
  recentTransactions,
  fetchUser,
  fetchTransactions,
  createPayment,
  refreshData,
} = useFinance();

// Initialize data on component mount
onMounted(() => {
  refreshData();
});

const handlePageChange = (page: number) => {
  fetchTransactions(page);
};

const handlePayment = async (payment: PaymentRequest) => {
  const result = await createPayment(payment);
  if (result) {
    // Success notification could be added here
    console.log('Payment successful:', result);
  }
};
</script>