<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const report = ref<any>(null)
const loading = ref(true)

const API_BASE = '/api'

onMounted(async () => {
  const res = await fetch(`${API_BASE}/submissions/${route.params.id}`)
  if (!res.ok) {
    router.push('/exercises')
    return
  }
  const data = await res.json()
  report.value = data
  loading.value = false
})

const bandColor = (band: string) => {
  if (!band) return 'bg-gray-100 text-gray-700'
  if (band.includes('优秀')) return 'bg-emerald-100 text-emerald-700'
  if (band.includes('良好')) return 'bg-blue-100 text-blue-700'
  if (band.includes('合格')) return 'bg-amber-100 text-amber-700'
  return 'bg-red-100 text-red-700'
}

const severityColor = (s: string) => {
  if (s === '严重') return 'text-red-600 bg-red-50'
  if (s === '中等') return 'text-amber-600 bg-amber-50'
  return 'text-gray-600 bg-gray-50'
}
</script>

<template>
  <div v-if="loading" class="text-center py-12 text-gray-500">加载报告...</div>
  <div v-else-if="!report" class="text-center py-12 text-gray-500">报告不存在</div>
  <div v-else class="max-w-3xl mx-auto space-y-6">
    <!-- 头部 -->
    <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
      <div class="flex items-center justify-between mb-4">
        <h1 class="text-xl font-bold text-gray-900">AI 评分报告</h1>
        <span class="text-xs text-gray-500">提交 #{{ report.id }}</span>
      </div>
      
      <div class="flex items-center gap-6">
        <div class="text-center">
          <div class="text-4xl font-bold text-indigo-600">{{ report.ai_score ?? '--' }}</div>
          <div class="text-sm text-gray-500">/ {{ report.ai_feedback?.max_score ?? 15 }} 分</div>
        </div>
        <div class="flex-1">
          <div class="flex items-center gap-2 mb-2">
            <span :class="['px-3 py-1 rounded-full text-sm font-medium', bandColor(report.ai_feedback?.band)]">
              {{ report.ai_feedback?.band ?? '评分中...' }}
            </span>
          </div>
          <p class="text-sm text-gray-600">
            {{ report.ai_feedback?.next_step ?? '报告生成中，请稍后再试' }}
          </p>
        </div>
      </div>
    </div>

    <!-- 策略聚焦 -->
    <div v-if="report.ai_feedback?.strategy_focus" class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
      <h2 class="font-semibold text-gray-900 mb-3">策略聚焦</h2>
      <div class="bg-indigo-50 rounded-lg p-4">
        <div class="text-sm font-medium text-indigo-900 mb-1">重点突破方向</div>
        <div class="text-sm text-indigo-700">{{ report.ai_feedback.strategy_focus }}</div>
      </div>
      <div v-if="report.ai_feedback?.first_fix" class="mt-3 text-sm text-gray-600">
        <span class="font-medium">首推修改：</span>{{ report.ai_feedback.first_fix }}
      </div>
    </div>

    <!-- 错误诊断 -->
    <div v-if="report.ai_feedback?.errors?.length" class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
      <h2 class="font-semibold text-gray-900 mb-4">错误诊断 ({{ report.ai_feedback.errors.length }})</h2>
      <div class="space-y-4">
        <div v-for="(err, idx) in report.ai_feedback.errors" :key="idx" class="border border-gray-100 rounded-lg p-4">
          <div class="flex items-center gap-3 mb-2">
            <span class="text-xs font-mono bg-gray-100 px-2 py-0.5 rounded">{{ err.code }}</span>
            <span class="text-sm font-medium text-gray-900">{{ err.category }}</span>
            <span :class="['text-xs px-2 py-0.5 rounded-full', severityColor(err.severity)]">{{ err.severity }}</span>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
            <div class="bg-red-50 rounded p-3">
              <div class="text-xs text-red-500 mb-1">你的译文</div>
              <div class="text-red-900">{{ err.student_text }}</div>
            </div>
            <div class="bg-emerald-50 rounded p-3">
              <div class="text-xs text-emerald-500 mb-1">建议修改</div>
              <div class="text-emerald-900">{{ err.suggestion }}</div>
            </div>
          </div>
          <div v-if="err.montreal_diagnosis" class="mt-2 text-xs text-gray-500">
            诊断：{{ err.montreal_diagnosis }}
          </div>
        </div>
      </div>
    </div>

    <!-- 表达建议 -->
    <div v-if="report.ai_feedback?.phrase_suggestions?.length" class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
      <h2 class="font-semibold text-gray-900 mb-4">表达升级</h2>
      <div class="space-y-3">
        <div v-for="(ph, idx) in report.ai_feedback.phrase_suggestions" :key="idx" class="bg-gray-50 rounded-lg p-4">
          <div class="text-sm text-gray-700 mb-2">原文：{{ ph.source }}</div>
          <div class="grid grid-cols-3 gap-2 text-sm">
            <div class="bg-white rounded p-2 border">
              <div class="text-xs text-gray-500">中性</div>
              <div class="text-gray-900">{{ ph.neutral }}</div>
            </div>
            <div class="bg-white rounded p-2 border">
              <div class="text-xs text-gray-500">正式</div>
              <div class="text-gray-900">{{ ph.formal }}</div>
            </div>
            <div class="bg-white rounded p-2 border">
              <div class="text-xs text-gray-500">口语</div>
              <div class="text-gray-900">{{ ph.colloquial }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 核心素养 -->
    <div v-if="report.ai_feedback?.core_competencies" class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
      <h2 class="font-semibold text-gray-900 mb-4">核心素养评估</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div v-for="(val, key) in report.ai_feedback.core_competencies" :key="key" class="text-center p-4 bg-gray-50 rounded-lg">
          <div class="text-xs text-gray-500 mb-1">{{ key }}</div>
          <div class="text-sm font-medium" :class="val === '达标' ? 'text-emerald-600' : 'text-amber-600'">{{ val }}</div>
        </div>
      </div>
    </div>

    <!-- 参考版本 -->
    <div v-if="report.ai_feedback?.reference_versions" class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
      <h2 class="font-semibold text-gray-900 mb-4">参考译文</h2>
      <div class="space-y-3">
        <div v-for="(text, key) in report.ai_feedback.reference_versions" :key="key" class="border border-gray-100 rounded-lg p-4">
          <div class="text-xs text-gray-500 mb-2 uppercase">{{ key }}</div>
          <div class="text-sm text-gray-900">{{ text }}</div>
        </div>
      </div>
    </div>

    <!-- 过程诊断 -->
    <div v-if="report.ai_feedback?.process_diagnosis" class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
      <h2 class="font-semibold text-gray-900 mb-2">过程诊断</h2>
      <p class="text-sm text-gray-600">{{ report.ai_feedback.process_diagnosis }}</p>
    </div>

    <!-- 操作 -->
    <div class="flex justify-between pt-4">
      <button @click="router.push('/exercises')" class="text-gray-500 hover:text-gray-700 text-sm">
        ← 返回练习列表
      </button>
      <button @click="router.push(`/exercises/${report.exercise_id}/practice`)" class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700">
        再练一次
      </button>
    </div>
  </div>
</template>
