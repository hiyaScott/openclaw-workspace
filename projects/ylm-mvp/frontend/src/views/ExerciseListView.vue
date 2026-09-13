<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const exercises = ref<any[]>([])
const loading = ref(true)

const API_BASE = '/api'

onMounted(async () => {
  // 初始化示例数据
  await fetch(`${API_BASE}/init-data`, { method: 'POST' }).catch(() => {})
  
  const res = await fetch(`${API_BASE}/exercises`)
  exercises.value = await res.json()
  loading.value = false
})

const goPractice = (id: number) => {
  router.push(`/exercises/${id}/practice`)
}

const difficultyColor = (d: string) => {
  const map: Record<string, string> = {
    beginner: 'bg-green-100 text-green-700',
    intermediate: 'bg-yellow-100 text-yellow-700',
    advanced: 'bg-red-100 text-red-700'
  }
  return map[d] || 'bg-gray-100 text-gray-700'
}

const difficultyLabel = (d: string) => {
  const map: Record<string, string> = {
    beginner: '入门',
    intermediate: '进阶',
    advanced: '高级'
  }
  return map[d] || d
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-900 mb-6">练习列表</h1>
    
    <div v-if="loading" class="text-center py-12 text-gray-500">
      加载中...
    </div>
    
    <div v-else class="space-y-4">
      <div 
        v-for="ex in exercises" 
        :key="ex.id"
        class="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition cursor-pointer"
        @click="goPractice(ex.id)"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h3 class="font-semibold text-gray-900">{{ ex.title }}</h3>
              <span :class="['text-xs px-2 py-0.5 rounded-full font-medium', difficultyColor(ex.difficulty)]">
                {{ difficultyLabel(ex.difficulty) }}
              </span>
            </div>
            <p class="text-sm text-gray-600 line-clamp-2">{{ ex.source_text }}</p>
            <div class="flex items-center gap-4 mt-3 text-xs text-gray-500">
              <span>{{ ex.text_type || '综合' }}</span>
              <span>{{ ex.direction === 'zh-en' ? '中译英' : '英译中' }}</span>
            </div>
          </div>
          <div class="ml-4">
            <div class="w-10 h-10 rounded-full bg-indigo-50 flex items-center justify-center text-indigo-600">
              →
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
