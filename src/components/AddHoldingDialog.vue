<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-2xl p-6 w-full max-w-md mx-4 shadow-2xl">
      <h2 class="text-2xl font-bold text-gray-800 mb-6">添加持仓基金</h2>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">基金代码</label>
          <input
            v-model="formData.fundCode"
            @blur="fetchFundName"
            type="text"
            placeholder="例如: 005550"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <p v-if="loadingName" class="text-xs text-blue-500 mt-1">正在获取基金名称...</p>
          <p v-if="nameError" class="text-xs text-red-500 mt-1">{{ nameError }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">基金名称</label>
          <input
            v-model="formData.fundName"
            type="text"
            placeholder="例如: 富国中证科创创业50ETF联接"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            :class="{ 'bg-gray-100 cursor-not-allowed': autoFilledName }"
            :disabled="autoFilledName"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">持仓金额 (元)</label>
          <input
            v-model.number="formData.amount"
            type="number"
            placeholder="例如: 10000"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">初始收益 (元)</label>
          <input
            v-model.number="formData.initialProfit"
            type="number"
            placeholder="例如: 500"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      <div class="flex gap-3 mt-8">
        <button
          @click="handleCancel"
          class="flex-1 px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors"
        >
          取消
        </button>
        <button
          @click="handleConfirm"
          :disabled="!isValid || loadingName"
          class="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          {{ loadingName ? '加载中...' : '确认添加' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { getFundName } from '../api/jqdata'

const props = defineProps({
  show: Boolean
})

const emit = defineEmits(['confirm', 'cancel'])

const formData = ref({
  fundCode: '',
  fundName: '',
  amount: '',
  initialProfit: ''
})

const loadingName = ref(false)
const nameError = ref('')
const autoFilledName = ref(false)

// 监听show变化，重置表单
watch(() => props.show, (newVal) => {
  if (!newVal) {
    resetForm()
  }
})

const isValid = computed(() => {
  return formData.value.fundCode &&
         formData.value.fundName &&
         formData.value.amount &&
         formData.value.amount > 0
})

async function fetchFundName() {
  if (!formData.value.fundCode || formData.value.fundCode.length < 6) {
    return
  }

  loadingName.value = true
  nameError.value = ''
  
  try {
    const data = await getFundName(formData.value.fundCode)
    if (data.fundName) {
      formData.value.fundName = data.fundName
      autoFilledName.value = true
    }
  } catch (error) {
    console.error('获取基金名称失败:', error)
    nameError.value = '未找到该基金，请手动输入基金名称'
    autoFilledName.value = false
  } finally {
    loadingName.value = false
  }
}

function handleConfirm() {
  if (isValid.value) {
    emit('confirm', { ...formData.value })
    resetForm()
  }
}

function handleCancel() {
  resetForm()
  emit('cancel')
}

function resetForm() {
  formData.value = {
    fundCode: '',
    fundName: '',
    amount: '',
    initialProfit: ''
  }
  loadingName.value = false
  nameError.value = ''
  autoFilledName.value = false
}
</script>

