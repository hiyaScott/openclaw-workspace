<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const exercise = ref<any>(null)
const loading = ref(true)
const currentStep = ref(1) // 1=分析 2=翻译 3=自审 4=自评

const API_BASE = '/api'

// 翻译前分析
const analysis = reactive({
  text_type: '',
  task_focus: '',
  risks: [] as string[]
})

// 译文
const translation = ref('')
const timeSpent = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

// 自审清单
const checklist = reactive({
  check_info: false,
  check_subject: false,
  check_logic: false,
  check_register: false,
  check_reading: false
})

// 自评
const selfAssessment = reactive({
  predicted_band: '',
  concern: '',
  uncertain_sentence: ''
})

onMounted(async () => {
  const res = await fetch(`${API_BASE}/exercises/${route.params.id}`)
  exercise.value = await res.json()
  loading.value = false
  
  // 开始计时
  timer = setInterval(() => timeSpent.value++, 1000)
})

const textTypeOptions = [
  '文化介绍类说明文本',
  '科技生活说明文本',
  '社会发展说明文本',
  '议题说明文本',
  '社会生活介绍文本',
  '文化+科技混合文本'
]

const taskOptions = [
  '准确传达事实',
  '解释原因结果',
  '展示文化特色',
  '概括发展变化'
]

const riskOptions = [
  '信息漏译',
  '主语选择',
  '逻辑关系',
  '语域不正式',
  '句子过散'
]

const toggleRisk = (risk: string) => {
  const idx = analysis.risks.indexOf(risk)
  if (idx > -1) analysis.risks.splice(idx, 1)
  else analysis.risks.push(risk)
}

const goStep = (step: number) => {
  currentStep.value = step
}

const submit = async () => {
  if (timer) clearInterval(timer)
  
  const res = await fetch(`${API_BASE}/submissions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      exercise_id: parseInt(route.params.id as string),
      student_translation: translation.value,
      time_spent_seconds: timeSpent.value,
      pre_analysis: {
        text_type: analysis.text_type,
        task_focus: analysis.task_focus,
        risks: analysis.risks
      },
      pre_submit_checklist: checklist,
      self_assessment: {
        predicted_band: selfAssessment.predicted_band,
        concern: selfAssessment.concern,
        uncertain_sentence: selfAssessment.uncertain_sentence
      }
    })
  })
  
  const data = await res.json()
  
  // 触发评分
  await fetch(`${API_BASE}/submissions/${data.id}/grade`, { method: 'POST' })
  
  // 跳转报告
  router.push(`/submissions/${data.id}/report`)
}
</script>

<template>
  <div v-if="loading" class="text-center py-12">加载中...</div>
  <div v-else class="max-w-3xl mx-auto">
    <!-- 步骤指示器 -->
    <div class="flex items-center justify-center mb-8">
      <div class="flex items-center space-x-2">
        <div v-for="i in 4" :key="i" class="flex items-center">
          <div :class="[
            'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium',
            currentStep >= i ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-500'
          ]">
            {{ i }}
          </div>
          <div v-if="i < 4" :class="['w-8 h-0.5', currentStep > i ? 'bg-indigo-600' : 'bg-gray-200']" />
        </div>
      </div>
    </div>

    <!-- 步骤1: 翻译前分析 -->
    <div v-if="currentStep === 1" class="bg-white rounded-xl p-6 shadow-sm border">
      <h2 class="text-lg font-semibold mb-4">翻译前分析（1分钟）</h2>
      
      <div class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">1. 文本类型判断</label>
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="opt in textTypeOptions"
              :key="opt"
              @click="analysis.text_type = opt"
              :class="[
                'px-4 py-2 rounded-lg text-sm text-left border transition',
                analysis.text_type === opt 
                  ? 'border-indigo-500 bg-indigo-50 text-indigo-700' 
                  : 'border-gray-200 hover:border-gray-300'
              ]"
            >
              {{ opt }}
            </button>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">2. 翻译任务定位</label>
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="opt in taskOptions"
              :key="opt"
              @click="analysis.task_focus = opt"
              :class="[
                'px-4 py-2 rounded-lg text-sm text-left border transition',
                analysis.task_focus === opt 
                  ? 'border-indigo-500 bg-indigo-50 text-indigo-700' 
                  : 'border-gray-200 hover:border-gray-300'
              ]"
            >
              {{ opt }}
            </button>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">3. 风险点识别（可多选）</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="opt in riskOptions"
              :key="opt"
              @click="toggleRisk(opt)"
              :class="[
                'px-3 py-1.5 rounded-full text-sm border transition',
                analysis.risks.includes(opt)
                  ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                  : 'border-gray-200 hover:border-gray-300'
              ]"
            >
              {{ opt }}
            </button>
          </div>
        </div>
      </div>

      <button 
        @click="goStep(2)"
        :disabled="!analysis.text_type || !analysis.task_focus"
        class="mt-6 w-full bg-indigo-600 text-white py-2.5 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        开始翻译 →
      </button>
    </div>

    <!-- 步骤2: 撰写译文 -->
    <div v-if="currentStep === 2" class="bg-white rounded-xl p-6 shadow-sm border">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold">撰写译文</h2>
        <span class="text-sm text-gray-500">用时: {{ Math.floor(timeSpent / 60) }}:{{ (timeSpent % 60).toString().padStart(2, '0') }}</span>
      </div>

      <div class="bg-gray-50 rounded-lg p-4 mb-4">
        <div class="text-xs text-gray-500 mb-1">原文</div>
        <p class="text-gray-900">{{ exercise.source_text }}</p>
      </div>

      <textarea
        v-model="translation"
        rows="8"
        class="w-full p-4 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
        placeholder="在此输入你的译文..."
      />

      <div class="flex justify-between mt-4">
        <button @click="goStep(1)" class="text-gray-500 hover:text-gray-700">← 返回分析</button>
        <button 
          @click="goStep(3)"
          :disabled="!translation.trim()"
          class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
        >
          下一步: 自审 →
        </button>
      </div>
    </div>

    <!-- 步骤3: 提交前自审 -->
    <div v-if="currentStep === 3" class="bg-white rounded-xl p-6 shadow-sm border">
      <h2 class="text-lg font-semibold mb-4">提交前自审清单</h2>
      
      <div class="space-y-3">
        <label class="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer">
          <input type="checkbox" v-model="checklist.check_info" class="mt-1 w-4 h-4 text-indigo-600">
          <div>
            <div class="font-medium text-gray-900">我检查了是否漏译核心信息</div>
            <div class="text-sm text-gray-500">核对原文每个信息点</div>
          </div>
        </label>
        <label class="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer">
          <input type="checkbox" v-model="checklist.check_subject" class="mt-1 w-4 h-4 text-indigo-600">
          <div>
            <div class="font-medium text-gray-900">我确定了英文句子的主语</div>
            <div class="text-sm text-gray-500">确保主语明确、不频繁切换</div>
          </div>
        </label>
        <label class="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer">
          <input type="checkbox" v-model="checklist.check_logic" class="mt-1 w-4 h-4 text-indigo-600">
          <div>
            <div class="font-medium text-gray-900">我显化了因果/转折/递进关系</div>
            <div class="text-sm text-gray-500">用连接词表达逻辑</div>
          </div>
        </label>
        <label class="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer">
          <input type="checkbox" v-model="checklist.check_register" class="mt-1 w-4 h-4 text-indigo-600">
          <div>
            <div class="font-medium text-gray-900">我避免了过口语表达</div>
            <div class="text-sm text-gray-500">保持说明性文本的正式度</div>
          </div>
        </label>
        <label class="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer">
          <input type="checkbox" v-model="checklist.check_reading" class="mt-1 w-4 h-4 text-indigo-600">
          <div>
            <div class="font-medium text-gray-900">我朗读了一遍英文译文</div>
            <div class="text-sm text-gray-500">通过耳朵发现拗口处</div>
          </div>
        </label>
      </div>

      <div class="flex justify-between mt-6">
        <button @click="goStep(2)" class="text-gray-500 hover:text-gray-700">← 返回修改</button>
        <button 
          @click="goStep(4)"
          class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700"
        >
          下一步: 自评 →
        </button>
      </div>
    </div>

    <!-- 步骤4: 提交后自评 -->
    <div v-if="currentStep === 4" class="bg-white rounded-xl p-6 shadow-sm border">
      <h2 class="text-lg font-semibold mb-4">提交后自评（30秒）</h2>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">1. 预测档位</label>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="band in ['7-9分', '10-12分', '13-15分']"
              :key="band"
              @click="selfAssessment.predicted_band = band"
              :class="[
                'px-4 py-2 rounded-lg text-sm border transition',
                selfAssessment.predicted_band === band
                  ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                  : 'border-gray-200 hover:border-gray-300'
              ]"
            >
              {{ band }}
            </button>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">2. 最担心哪一项</label>
          <select v-model="selfAssessment.concern" class="w-full p-2.5 border border-gray-200 rounded-lg">
            <option value="">请选择...</option>
            <option value="意义传递">意义传递</option>
            <option value="译入语规范">译入语规范</option>
            <option value="文笔质量">文笔质量</option>
            <option value="不确定">不确定</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">3. 最不确定的句子</label>
          <textarea
            v-model="selfAssessment.uncertain_sentence"
            rows="3"
            class="w-full p-3 border border-gray-200 rounded-lg resize-none"
            placeholder="粘贴你最不确定的句子..."
          />
        </div>
      </div>

      <div class="flex justify-between mt-6">
        <button @click="goStep(3)" class="text-gray-500 hover:text-gray-700">← 返回</button>
        <button 
          @click="submit"
          class="bg-indigo-600 text-white px-8 py-2.5 rounded-lg font-medium hover:bg-indigo-700"
        >
          提交并查看反馈
        </button>
      </div>
    </div>
  </div>
</template>
