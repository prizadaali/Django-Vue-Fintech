<template>
  <div class="bg-white rounded-xl shadow-lg p-6">
    <h3 class="text-lg font-semibold text-gray-900 mb-6">Send Payment</h3>
    
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label for="amount" class="block text-sm font-medium text-gray-700 mb-2">
          Amount
        </label>
        <div class="relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <span class="text-gray-500 sm:text-sm">$</span>
          </div>
          <input
            id="amount"
            v-model="form.amount"
            type="number"
            step="0.01"
            min="0.01"
            required
            class="block w-full pl-7 pr-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            placeholder="0.00"
          />
        </div>
        <p v-if="errors.amount" class="mt-1 text-sm text-red-600">{{ errors.amount }}</p>
      </div>

      <div>
        <label for="recipientAccount" class="block text-sm font-medium text-gray-700 mb-2">
          Recipient Account
        </label>
        <input
          id="recipientAccount"
          v-model="form.recipientAccount"
          type="text"
          required
          class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          placeholder="Enter account number"
        />
        <p v-if="errors.recipientAccount" class="mt-1 text-sm text-red-600">
          {{ errors.recipientAccount }}
        </p>
      </div>

      <div>
        <label for="category" class="block text-sm font-medium text-gray-700 mb-2">
          Category
        </label>
        <select
          id="category"
          v-model="form.category"
          required
          class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        >
          <option value="">Select category</option>
          <option value="transfer">Transfer</option>
          <option value="payment">Payment</option>
          <option value="shopping">Shopping</option>
          <option value="bills">Bills</option>
          <option value="other">Other</option>
        </select>
        <p v-if="errors.category" class="mt-1 text-sm text-red-600">{{ errors.category }}</p>
      </div>

      <div>
        <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
          Description
        </label>
        <input
          id="description"
          v-model="form.description"
          type="text"
          required
          class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          placeholder="Payment description"
        />
        <p v-if="errors.description" class="mt-1 text-sm text-red-600">
          {{ errors.description }}
        </p>
      </div>

      <div class="pt-4">
        <button
          type="submit"
          :disabled="loading"
          class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
        >
          <div v-if="loading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
          {{ loading ? 'Processing...' : 'Send Payment' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import type { PaymentRequest } from '@/types';

interface Props {
  loading: boolean;
}

interface Emits {
  (e: 'submit', payment: PaymentRequest): void;
}

defineProps<Props>();
const emit = defineEmits<Emits>();

const form = reactive<PaymentRequest>({
  amount: 0,
  recipientAccount: '',
  description: '',
  category: '',
});

const errors = ref<Record<string, string>>({});

const validateForm = (): boolean => {
  errors.value = {};

  if (form.amount <= 0) {
    errors.value.amount = 'Amount must be greater than 0';
  }

  if (!form.recipientAccount.trim()) {
    errors.value.recipientAccount = 'Recipient account is required';
  } else if (form.recipientAccount.length < 8) {
    errors.value.recipientAccount = 'Invalid account number';
  }

  if (!form.category) {
    errors.value.category = 'Category is required';
  }

  if (!form.description.trim()) {
    errors.value.description = 'Description is required';
  }

  return Object.keys(errors.value).length === 0;
};

const handleSubmit = () => {
  if (validateForm()) {
    emit('submit', { ...form });
    resetForm();
  }
};

const resetForm = () => {
  form.amount = 0;
  form.recipientAccount = '';
  form.description = '';
  form.category = '';
  errors.value = {};
};
</script>