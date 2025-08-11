<template>
  <div class="bg-gradient-to-r from-blue-600 to-blue-700 rounded-xl p-6 text-white shadow-lg">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-blue-100 text-sm font-medium mb-1">Current Balance</p>
        <p class="text-3xl font-bold">{{ formattedBalance }}</p>
        <p class="text-blue-200 text-sm mt-1">Account: {{ user?.accountNumber }}</p>
      </div>
      <div class="bg-white bg-opacity-20 rounded-lg p-3">
        <CreditCardIcon class="h-8 w-8 text-white" />
      </div>
    </div>
    
    <div class="mt-4 pt-4 border-t border-blue-500 border-opacity-30">
      <div class="flex items-center justify-between text-sm">
        <span class="text-blue-200">Available</span>
        <span class="text-white font-medium">{{ formattedBalance }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { CreditCardIcon } from '@heroicons/vue/24/outline';
import type { User } from '@/types';

interface Props {
  user: User | null;
  formattedBalance: string;
}

defineProps<Props>();
</script>