const fs = require('fs');

const html = fs.readFileSync('fund_page.html', 'utf-8');

// 查找 stockCodesNew 变量
const regex = /var\s+stockCodesNew\s*=\s*(\[.*?\]);/s;
const match = html.match(regex);

if (match && match[1]) {
  console.log('找到stockCodesNew变量');
  console.log('前500字符:', match[1].substring(0, 500));
  
  try {
    const data = JSON.parse(match[1]);
    console.log('解析成功，数组长度:', data.length);
    if (data.length > 0) {
      console.log('第一个元素:', JSON.stringify(data[0], null, 2));
      console.log('前3个元素:');
      data.slice(0, 3).forEach((item, i) => {
        console.log(`[${i}]:`, JSON.stringify(item, null, 2));
      });
    }
  } catch (e) {
    console.error('解析失败:', e.message);
  }
} else {
  console.log('未找到stockCodesNew变量');
}
