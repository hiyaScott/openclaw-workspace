<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const submissions = ref<any[]>([])
const loading = ref(true)

const API_BASE = '/api'

onMounted(async () => {
  // 由于没有专门的列表接口，这里先mock展示
  // MVP阶段简化为从localStorage或提示用户
  loading.value = false
})

const goPractice = () => router.push('/exercises')
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-900 mb-6">练习历史</h1>
    
    <div class="bg-white rounded-xl p-8 shadow-sm border border-gray-100 text-center">
      <div class="text-4xl mb-4">📝</div>
      <h2 class="text-lg font-medium text-gray-900 mb-2">历史记录功能开发中</h2>
      <p class="text-sm text-gray-500 mb-6 max-w-md mx-auto">
        MVP 阶段暂仅支持单条报告查看。完成练习后，可通过报告页面查看详细反馈。
      </p>
      <button 
        @click="goPractice"
        class="bg-indigo-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-indigo-700 transition"
      >
        去练习
      </button>
    </div>
  </div>
</template>
