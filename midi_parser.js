const fs = require('fs');

// MIDI音符到频率映射
function midiToFreq(note) {
    return 440 * Math.pow(2, (note - 69) / 12);
}

const noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
function midiToNote(note) {
    const octave = Math.floor(note / 12) - 1;
    return noteNames[note % 12] + octave;
}

// 解析MIDI
function parseMidi(data) {
    let pos = 0;
    const read8 = () => data[pos++];
    const read16 = () => (read8() << 8) | read8();
    const read32 = () => (read16() << 16) | read16();
    const readVar = () => {
        let val = 0, byte;
        do { byte = read8(); val = (val << 7) | (byte & 0x7F); } while (byte & 0x80);
        return val;
    };

    // Header
    const header = String.fromCharCode(...data.slice(0, 4));
    if (header !== 'MThd') throw new Error('Not MIDI');
    pos = 4;
    read32(); // length
    read16(); // format
    const trackCount = read16();
    const timeDiv = read16();

    const allNotes = [];
    const C1_TO_ARP = { 24: '1', 26: '2', 28: '3', 29: '4', 31: '5', 33: '6', 34: 'b7' };
    const CHORD_LIB = {
        '1': { notes: [65.41, 98.00, 130.81, 164.81] },
        '2': { notes: [73.42, 110.00, 146.83, 174.61] },
        '3': { notes: [82.41, 123.47, 164.81, 196.00] },
        '4': { notes: [87.31, 130.81, 174.61, 220.00] },
        '5': { notes: [98.00, 146.83, 196.00, 246.94] },
        '6': { notes: [110.00, 164.81, 220.00, 261.63] },
        'b7': { notes: [116.54, 174.61, 233.08, 293.66] }
    };
    const EIGHTH_MS = 600;

    // Parse tracks
    for (let t = 0; t < trackCount; t++) {
        const trkHdr = String.fromCharCode(...data.slice(pos, pos + 4));
        if (trkHdr !== 'MTrk') { console.log('Skip track', t); break; }
        pos += 4;
        const trkLen = read32();
        const trkEnd = pos + trkLen;
        
        let time = 0, status = 0;
        while (pos < trkEnd) {
            const delta = readVar();
            time += delta;
            let st = read8();
            if (st < 0x80) { st = status; pos--; }
            else status = st;
            
            const type = st & 0xF0;
            if (type === 0x90) {
                const note = read8();
                const vel = read8();
                if (vel > 0) {
                    const timeMs = Math.round(time * (60000 / 120 / timeDiv));
                    if (note >= 24 && note <= 35 && C1_TO_ARP[note]) {
                        const chord = CHORD_LIB[C1_TO_ARP[note]];
                        for (let i = 0; i < 4; i++) {
                            allNotes.push({ note: 'C', freq: chord.notes[i], isSide: false, time: timeMs + i * EIGHTH_MS, isArpeggio: true });
                        }
                    } else if (note >= 48 && note <= 84) {
                        allNotes.push({ note: midiToNote(note), freq: midiToFreq(note), isSide: false, time: timeMs });
                    }
                }
            } else if (type === 0x80) { read8(); read8(); }
            else if (type === 0xB0 || type === 0xC0 || type === 0xD0) read8();
            else if (type === 0xE0) { read8(); read8(); }
            else if (st === 0xFF) {
                const mt = read8(), ml = readVar();
                if (mt === 0x2F) break;
                pos += ml;
            } else if (st === 0xF0 || st === 0xF7) pos += readVar();
        }
    }

    allNotes.sort((a, b) => a.time - b.time);
    if (allNotes.length > 0) {
        const first = allNotes[0].time;
        allNotes.forEach(n => n.time -= first);
    }
    return allNotes;
}

// 主程序
const file = process.argv[2];
const name = process.argv[3];
if (!file) { console.log('Usage: node midi_parser.js <midi_file> <song_name>'); process.exit(1); }

const data = fs.readFileSync(file);
const notes = parseMidi(data);

const id = name.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '').toLowerCase().substring(0, 20);
const lastTime = notes.length > 0 ? notes[notes.length - 1].time : 0;

console.log(`
        '${id}': {
            id: '${id}',
            name: '${name}',
            description: '经典曲目 · ${notes.length}个音符 · MIDI导入',
            tempo: ${Math.round(lastTime / notes.length * 2) || 600},
            notes: [`);

for (const n of notes) {
    const arp = n.isArpeggio ? ', isArpeggio: true' : '';
    console.log(`                { note: '${n.note}', freq: ${n.freq.toFixed(2)}, isSide: ${n.isSide}, time: ${n.time}${arp} },`);
}

console.log(`            ]
        },`);
