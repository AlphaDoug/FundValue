const axios = require('axios');
const fs = require('fs');

async function findHoldingsVariable() {
  try {
    console.log('正在请求东方财富基金页面...');
    const response = await axios.get('https://fund.eastmoney.com/000001.html', {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });

    // 保存页面内容到文件
    fs.writeFileSync('fund_page.html', response.data, 'utf-8');
    console.log('页面已保存到 fund_page.html');

    // 查找所有 var 开头的变量声明
    const varRegex = /var\s+(\w+)\s*=/g;
    const variables = [];
    let match;
    
    while ((match = varRegex.exec(response.data)) !== null) {
      variables.push(match[1]);
    }

    console.log('\n找到的所有变量名:');
    const holdingRelated = variables.filter(v => 
      v.toLowerCase().includes('holding') || 
      v.toLowerCase().includes('stock') ||
      v.toLowerCase().includes('cc')
    );
    
    console.log('持仓相关变量:', holdingRelated.join(', '));

    // 查找JSON数组
    const jsonArrayRegex = /\[\{.*?\}\]/g;
    const jsonArrays = [];
    let arrayMatch;
    
    while ((arrayMatch = jsonArrayRegex.exec(response.data)) !== null) {
      const str = arrayMatch[0];
      if (str.includes('stock') || str.includes('Stock') || str.includes('代码')) {
        jsonArrays.push({
          start: arrayMatch.index,
          length: str.length,
          preview: str.substring(0, 200)
        });
      }
    }

    console.log('\n包含"stock"的JSON数组数量:', jsonArrays.length);
    if (jsonArrays.length > 0) {
      console.log('第一个数组预览:', jsonArrays[0].preview);
    }

  } catch (error) {
    console.error('错误:', error.message);
  }
}

findHoldingsVariable();
