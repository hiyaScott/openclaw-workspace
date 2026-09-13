<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goToExercises = () => router.push('/exercises')
</script>

<template>
  <div class="space-y-8">
    <!-- Hero -->
    <div class="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
      <h1 class="text-3xl font-bold text-gray-900 mb-3">
        译了么 — 翻译能力训练场
      </h1>
      <p class="text-gray-600 mb-6 max-w-2xl">
        这不是一个"查答案"的工具，而是一个"练判断"的训练场。
        通过结构化反馈和反思循环，培养真正的翻译能力。
      </p>
      <button 
        @click="goToExercises"
        class="bg-indigo-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-indigo-700 transition"
      >
        开始练习
      </button>
    </div>

    <!-- 学习闭环 -->
    <div class="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
      <h2 class="text-lg font-semibold text-gray-900 mb-6">蒙特雷式学习循环</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="text-center p-4 bg-indigo-50 rounded-xl">
          <div class="text-2xl mb-2">📋</div>
          <div class="font-medium text-gray-900">接稿分析</div>
          <div class="text-xs text-gray-500 mt-1">先分析再翻译</div>
        </div>
        <div class="text-center p-4 bg-blue-50 rounded-xl">
          <div class="text-2xl mb-2">✍️</div>
          <div class="font-medium text-gray-900">撰写译文</div>
          <div class="text-xs text-gray-500 mt-1">初稿翻译</div>
        </div>
        <div class="text-center p-4 bg-amber-50 rounded-xl">
          <div class="text-2xl mb-2">🔍</div>
          <div class="font-medium text-gray-900">自审自评</div>
          <div class="text-xs text-gray-500 mt-1">建立判断力</div>
        </div>
        <div class="text-center p-4 bg-emerald-50 rounded-xl">
          <div class="text-2xl mb-2">📊</div>
          <div class="font-medium text-gray-900">AI反馈</div>
          <div class="text-xs text-gray-500 mt-1">结构化诊断</div>
        </div>
      </div>
    </div>
  </div>
</template>
