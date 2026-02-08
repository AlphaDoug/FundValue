const fs = require('fs');

const html = fs.readFileSync('fund_page.html', 'utf-8');

// 查找所有包含持仓的数据
const patterns = [
  /Data_StockF10Holdings/g,
  /Data_CCF10Holdings/g,
  /stockF10Holdings/g,
  /持仓明细/g,
  /持仓股票/g
];

console.log('搜索持仓数据...');

for (const pattern of patterns) {
  const matches = html.match(pattern);
  if (matches) {
    console.log(`找到匹配 "${pattern}":`, matches.length, '次');
  }
}

// 查找包含股票名称和代码的JSON
const stockDataRegex = /\{[^}]*"stock"[^}]*"name"[^}]*\}/g;
const stockMatches = html.match(stockDataRegex);
if (stockMatches) {
  console.log('\n找到包含stock和name的JSON对象:', stockMatches.length, '个');
  console.log('第一个示例:', stockMatches[0]);
}

// 查找包含"代码"的JSON
const codeDataRegex = /\{[^}]*"代码"[^}]*\}/g;
const codeMatches = html.match(codeDataRegex);
if (codeMatches) {
  console.log('\n找到包含"代码"的JSON对象:', codeMatches.length, '个');
  console.log('第一个示例:', codeMatches[0]);
}

// 搜索A股持仓相关内容
const aStockRegex = /A股持仓/g;
const aStockMatches = html.match(aStockRegex);
if (aStockMatches) {
  console.log('\n找到"A股持仓":', aStockMatches.length, '次');
}

// 打印页面中所有 var 声明
const varDeclarations = [];
const varRegex = /var\s+(\w+)\s*=/g;
let match;
let count = 0;
while ((match = varRegex.exec(html)) !== null && count < 50) {
  varDeclarations.push(match[1]);
  count++;
}

console.log('\n前50个变量名:');
varDeclarations.forEach(v => {
  if (v.toLowerCase().includes('holding') || 
      v.toLowerCase().includes('stock') ||
      v.toLowerCase().includes('cc') ||
      v.toLowerCase().includes('position') ||
      v.toLowerCase().includes('asset')) {
    console.log('  *', v);
  }
});
