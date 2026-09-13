<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 导航栏 -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-5xl mx-auto px-4 sm:px-6">
        <div class="flex justify-between h-14">
          <div class="flex items-center">
            <RouterLink to="/" class="text-lg font-bold text-indigo-600">
              译了么 MVP
            </RouterLink>
          </div>
          <div class="flex items-center space-x-6">
            <RouterLink to="/exercises" class="text-sm text-gray-600 hover:text-indigo-600 transition">
              练习
            </RouterLink>
            <RouterLink to="/history" class="text-sm text-gray-600 hover:text-indigo-600 transition">
              历史
            </RouterLink>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容 -->
    <main class="max-w-5xl mx-auto px-4 sm:px-6 py-6">
      <RouterView />
    </main>
  </div>
</template>
