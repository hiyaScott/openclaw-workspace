// 临时脚本：解析0408成绩文件
const XLSX = require('xlsx');
const fs = require('fs');

// 读取数学表
const mathBuf = fs.readFileSync('/root/.openclaw/media/inbound/0408Math---a7b34a81-282c-477a-a883-22d089bec3d7.xlsx');
const mathWB = XLSX.read(mathBuf, { type: 'buffer' });
const mathSheet = mathWB.Sheets[mathWB.SheetNames[0]];
const mathData = XLSX.utils.sheet_to_json(mathSheet, { header: 1 });

console.log('=== 数学表结构 ===');
console.log('总行数:', mathData.length);
console.log('前5行:', mathData.slice(0, 5));

// 提取考号-成绩对
const mathScores = [];
for (let i = 1; i < mathData.length; i++) {
    const row = mathData[i];
    if (!row) continue;
    // 每3列一组: 考号, 成绩, 空
    for (let j = 0; j < row.length; j += 3) {
        const id = row[j]?.toString().trim();
        const score = parseFloat(row[j + 1]);
        if (id && /^[A-Z]\d{3}$/.test(id)) {
            mathScores.push({ id, score });
        }
    }
}

console.log('\n=== 数学成绩 ===');
console.log('总记录数:', mathScores.length);

// 找K115
const k115 = mathScores.find(s => s.id === 'K115');
console.log('K115:', k115 || '未找到');

// 找0分的
const zeroScores = mathScores.filter(s => s.score === 0);
console.log('0分学生数:', zeroScores.length);
console.log('0分考号:', zeroScores.map(s => s.id));

// 读英语表
const engBuf = fs.readFileSync('/root/.openclaw/media/inbound/0408Eng---322e2362-0083-411e-aa09-7958151478bb.xlsx');
const engWB = XLSX.read(engBuf, { type: 'buffer' });
const engSheet = engWB.Sheets[engWB.SheetNames[0]];
const engData = XLSX.utils.sheet_to_json(engSheet, { header: 1 });

const engScores = [];
for (let i = 3; i < engData.length; i++) { // 英语表从第4行开始
    const row = engData[i];
    if (!row) continue;
    for (let j = 0; j < row.length; j += 3) {
        const id = row[j]?.toString().trim();
        const score = parseFloat(row[j + 1]);
        if (id && /^[A-Z]\d{3}$/.test(id)) {
            engScores.push({ id, score });
        }
    }
}

console.log('\n=== 英语成绩 ===');
console.log('总记录数:', engScores.length);

// 对比
const mathIds = new Set(mathScores.map(s => s.id));
const engIds = new Set(engScores.map(s => s.id));

console.log('\n=== 对比 ===');
console.log('只在数学中:', [...mathIds].filter(id => !engIds.has(id)));
console.log('只在英语中:', [...engIds].filter(id => !mathIds.has(id)));

// 检查K115的详细情况
const k115Math = mathScores.find(s => s.id === 'K115');
const k115Eng = engScores.find(s => s.id === 'K115');
console.log('\nK115 数学成绩:', k115Math ? k115Math.score : '无');
console.log('K115 英语成绩:', k115Eng ? k115Eng.score : '无');
