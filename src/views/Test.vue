<template>
  <div class="p-4">
    <h1 class="text-xl font-bold mb-4">测试页面</h1>

    <div class="mb-4">
      <button @click="testAPI" class="px-4 py-2 bg-blue-500 text-white rounded">
        测试API
      </button>
    </div>

    <div class="bg-white p-4 rounded shadow">
      <h2 class="font-bold mb-2">结果:</h2>
      <pre class="text-sm">{{ result }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const result = ref('点击按钮测试API')

async function testAPI() {
  try {
    result.value = '正在测试...'
    console.log('开始测试API')

    const response = await axios.get('http://localhost:8000/api/health')
    result.value = JSON.stringify(response.data, null, 2)
    console.log('测试成功:', response.data)
  } catch (error) {
    result.value = '错误: ' + error.message
    console.error('测试失败:', error)
  }
}
</script>
