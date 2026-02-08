const axios = require('axios');

async function testFundHoldings() {
  try {
    console.log('正在请求东方财富基金页面...');
    const response = await axios.get('https://fund.eastmoney.com/000001.html', {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });

    console.log('页面状态:', response.status);
    console.log('页面内容长度:', response.data.length);

    // 查找持仓数据
    const holdingsRegex = /var\s+Data_stockF10Holdings\s*=\s*(\[.*?\]);/s;
    const match = response.data.match(holdingsRegex);

    if (match && match[1]) {
      console.log('找到持仓数据，长度:', match[1].length);
      console.log('前300个字符:', match[1].substring(0, 300));
      
      try {
        const holdings = JSON.parse(match[1]);
        console.log('解析成功，持仓数量:', holdings.length);
        if (holdings.length > 0) {
          console.log('第一个持仓:', JSON.stringify(holdings[0], null, 2));
        }
      } catch (parseError) {
        console.error('JSON解析失败:', parseError.message);
      }
    } else {
      console.log('未找到持仓数据，尝试其他变量名...');
      
      // 查找其他可能的变量名
      const possiblePatterns = [
        /var\s+Data_StockF10Holdings\s*=\s*(\[.*?\]);/s,
        /var\s+Data_stockholding\s*=\s*(\[.*?\]);/s,
        /var\s+Data_CCF10Holdings\s*=\s*(\[.*?\]);/s,
        /stockF10Holdings:\s*(\[.*?\]),/s,
      ];
      
      for (let i = 0; i < possiblePatterns.length; i++) {
        const patternMatch = response.data.match(possiblePatterns[i]);
        if (patternMatch && patternMatch[1]) {
          console.log(`找到匹配模式 ${i + 1}`);
          console.log('前200字符:', patternMatch[1].substring(0, 200));
          break;
        }
      }
      
      // 搜索包含持仓关键词的内容
      if (response.data.includes('持仓')) {
        console.log('页面包含"持仓"关键词');
      }
    }
  } catch (error) {
    console.error('错误:', error.message);
  }
}

testFundHoldings();
