const fs = require('fs');

// 编钟频率映射表
const bellFreqMap = {
    130.81: 'C3', 146.83: 'D3', 164.81: 'E3', 196.00: 'G3', 220.00: 'A3',
    261.63: 'C4', 293.66: 'D4', 329.63: 'E4', 392.00: 'G4', 440.00: 'A4',
    523.25: 'C5', 587.33: 'D5', 659.25: 'E5', 783.99: 'G5', 880.00: 'A5'
};

// 侧敲频率映射
const sideFreqMap = {
    246.94: 'G3', 493.88: 'G4', 987.77: 'G5',  // B notes
    174.61: 'D3', 349.23: 'D4', 698.46: 'D5',  // F notes
    164.81: 'E3', 329.63: 'E4', 659.25: 'E5'   // E side notes
};

// 琶音音符映射到最近的编钟音（用于动画）
const arpeggioToBell = {
    // C和弦琶音: C2-G2-C3-E3 -> 映射到 C3, G3, C4, E4
    65.41: 'C3', 98.00: 'G3', 130.81: 'C4', 164.81: 'E4',
    // Dm和弦琶音: D2-A2-D3-F3 -> 映射到 D3, A3, D4, F4(D侧敲)
    73.42: 'D3', 110.00: 'A3', 146.83: 'D4', 174.61: 'D4',
    // Em和弦琶音: E2-B2-E3-G3 -> 映射到 E3, G3(E侧敲?), E4, G4
    82.41: 'E3', 123.47: 'E3', 164.81: 'E4', 196.00: 'G4',
    // F和弦琶音: F2-C3-F3-A3 -> 映射到 G3(F->G?), C4, G4, A4
    87.31: 'G3', 130.81: 'C4', 174.61: 'G4', 220.00: 'A4',
    // G和弦琶音: G2-D3-G3-B3 -> 映射到 G3, D4(G侧敲?), G4, G4(B->G侧敲)
    98.00: 'G3', 146.83: 'G3', 196.00: 'G4', 246.94: 'G4',
    // Am和弦琶音: A2-E3-A3-C4 -> 映射到 A3, E4, A4, C5
    110.00: 'A3', 164.81: 'E4', 220.00: 'A4', 261.63: 'C5',
    // Bb和弦琶音: Bb2-F3-Bb3-D4 -> 映射到 A3(Bb->A), D4(F->D侧敲?), A4, D5
    116.54: 'A3', 174.61: 'D4', 233.08: 'A4', 293.66: 'D5'
};

function getNoteForAnimation(freq, isArpeggio) {
    // 如果是琶音，使用映射表
    if (isArpeggio && arpeggioToBell[freq]) {
        return arpeggioToBell[freq];
    }
    // 否则查找标准编钟频率
    if (bellFreqMap[freq]) {
        return bellFreqMap[freq];
    }
    // 查找最接近的编钟音
    let closest = null;
    let minDiff = Infinity;
    for (const [f, note] of Object.entries(bellFreqMap)) {
        const diff = Math.abs(freq - parseFloat(f));
        if (diff < minDiff) {
            minDiff = diff;
            closest = note;
        }
    }
    return closest || 'C4';
}

// 读取文件
const file = process.argv[2];
const content = fs.readFileSync(file, 'utf8');

// 修复音符映射
let fixed = content.replace(/\{ note: 'C', freq: ([\d.]+), isSide: (false|true), time: (\d+), isArpeggio: true \}/g, (match, freq, isSide, time) => {
    const note = getNoteForAnimation(parseFloat(freq), true);
    return `{ note: '${note}', freq: ${freq}, isSide: ${isSide}, time: ${time}, isArpeggio: true }`;
});

// 修复非琶音但note为'C'的情况
fixed = fixed.replace(/\{ note: 'C', freq: ([\d.]+), isSide: (false|true), time: (\d+) \}/g, (match, freq, isSide, time) => {
    const note = getNoteForAnimation(parseFloat(freq), false);
    return `{ note: '${note}', freq: ${freq}, isSide: ${isSide}, time: ${time} }`;
});

fs.writeFileSync(file, fixed);
console.log('Fixed MIDI note mappings');
