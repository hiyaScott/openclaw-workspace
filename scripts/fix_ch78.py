import re, os

BASE = '/root/.openclaw/workspace/portfolio-blog/research/junior-physics/courseware-physics'

EXAMPLE_HTML = '''
<h3>✏️ 例题 {n}</h3>
<div class="example-item" onclick="this.classList.toggle('expanded')">
  <div class="q">📌 例题 {n}：（补充例题，请根据本单元内容设计）</div>
  <div class="a">
    <strong>解：</strong>待补充
    <div class="step">💡 请根据课堂内容补充详细解答</div>
  </div>
</div>'''

QUIZ_HTML = '''<h3>🎯 随堂测验 Q{n}</h3>
<div id="q_{u}_{n}">
  <p><strong>Q{n}.</strong> （请根据本单元内容设计测试题）</p>
  <button class="quiz-option" onclick="checkQ_{u}_{n}(this,'A')">A. 选项A</button>
  <button class="quiz-option" onclick="checkQ_{u}_{n}(this,'B')">B. 选项B</button>
  <button class="quiz-option" onclick="checkQ_{u}_{n}(this,'C')">C. 选项C</button>
  <div class="feedback" id="fb_{u}_{n}"></div>
</div>
<script>function checkQ_{u}_{n}(btn, ans) {
  const fb = document.getElementById('fb_{u}_{n}');
  const opts = document.querySelectorAll('#q_{u}_{n} .quiz-option');
  opts.forEach(o => { o.classList.remove('correct','wrong'); });
  if(ans === 'A') { btn.classList.add('correct'); fb.className = 'feedback ok'; fb.textContent = '正确！'; }
  else { btn.classList.add('wrong'); fb.className = 'feedback wrong'; fb.textContent = '不对，再想想。'; }
}</script>'''

SVG_TEMPLATES = {
    'ch07': [
        '''<h3>🧪 实验 1：浮力与排水体积</h3>
<div class="demo-box">
  <canvas id="buoyancyCanvas" width="500" height="250"></canvas>
  <div class="slider-control">
    <label>浸入深度</label>
    <input type="range" id="submerge" min="0" max="100" value="50">
    <span class="value" id="subVal">50%</span>
  </div>
  <p style="font-size:12px;color:var(--text-dim);margin-top:8px">拖动滑块改变浸入深度，观察浮力变化。F浮 = ρ液gV排</p>
</div>
<script>
(function(){
  const c = document.getElementById('buoyancyCanvas'); if(!c) return;
  const ctx = c.getContext('2d');
  const sInput = document.getElementById('submerge');
  const sVal = document.getElementById('subVal');
  function draw() {
    let pct = sInput ? parseInt(sInput.value) : 50;
    if(sVal) sVal.textContent = pct + '%';
    ctx.clearRect(0,0,500,250);
    ctx.fillStyle = 'rgba(0,200,255,0.3)'; ctx.fillRect(50,120,400,120);
    let h = 100 * pct / 100;
    ctx.fillStyle = 'var(--accent)'; ctx.fillRect(200, 120-h, 100, 100);
    ctx.fillStyle = 'rgba(0,200,255,0.6)'; ctx.fillRect(200, 120, 100, h);
    ctx.fillStyle = 'var(--text)'; ctx.font = '14px monospace';
    ctx.fillText('V排 = ' + pct + '%', 350, 100);
    requestAnimationFrame(draw);
  }
  draw();
})();
</script>''',
        '''<h3>🧪 实验 2：物体浮沉条件</h3>
<div class="demo-box">
  <canvas id="floatCanvas" width="500" height="250"></canvas>
  <div style="margin-top:10px">
    <button class="btn" onclick="setObj('wood')">🪵 木块 (ρ<水)</button>
    <button class="btn btn-ghost" onclick="setObj('iron')">🔩 铁块 (ρ>水)</button>
    <button class="btn btn-ghost" onclick="setObj('ship')">🚢 轮船 (空心)</button>
  </div>
  <p style="font-size:12px;color:var(--text-dim);margin-top:8px">选择不同物体，观察浮沉状态。</p>
</div>
<script>
(function(){
  const c = document.getElementById('floatCanvas'); if(!c) return;
  const ctx = c.getContext('2d');
  let objType = 'wood';
  window.setObj = function(t) { objType = t; };
  function draw() {
    ctx.clearRect(0,0,500,250);
    ctx.fillStyle = 'rgba(0,200,255,0.3)'; ctx.fillRect(50,120,400,120);
    let y = objType === 'iron' ? 140 : objType === 'ship' ? 80 : 60;
    ctx.fillStyle = objType === 'iron' ? '#888' : objType === 'ship' ? '#555' : '#8B4513';
    ctx.fillRect(200, y, objType==='ship'?120:60, objType==='ship'?40:60);
    ctx.fillStyle = 'var(--text)'; ctx.font = '14px monospace';
    ctx.fillText(objType==='iron'?'下沉':objType==='ship'?'漂浮':'漂浮', 350, 50);
    requestAnimationFrame(draw);
  }
  draw();
})();
</script>''',
    ],
    'ch08': [
        '''<h3>🧪 实验 1：杠杆平衡条件</h3>
<div class="demo-box">
  <canvas id="leverCanvas" width="500" height="250"></canvas>
  <div class="slider-control">
    <label>阻力臂 L₂</label>
    <input type="range" id="resistArm" min="50" max="200" value="120">
    <span class="value" id="armVal">120 mm</span>
  </div>
  <p style="font-size:12px;color:var(--text-dim);margin-top:8px">拖动滑块改变阻力臂，观察杠杆倾斜。F₁L₁ = F₂L₂</p>
</div>
<script>
(function(){
  const c = document.getElementById('leverCanvas'); if(!c) return;
  const ctx = c.getContext('2d');
  const aInput = document.getElementById('resistArm');
  const aVal = document.getElementById('armVal');
  function draw() {
    let L2 = aInput ? parseInt(aInput.value) : 120;
    if(aVal) aVal.textContent = L2 + ' mm';
    ctx.clearRect(0,0,500,250);
    let pivot = 250, angle = (L2 - 100) * 0.003;
    ctx.strokeStyle = 'var(--accent)'; ctx.lineWidth = 4;
    ctx.beginPath(); ctx.moveTo(pivot - 150*Math.cos(angle), 150 + 150*Math.sin(angle));
    ctx.lineTo(pivot + L2*Math.cos(angle), 150 - L2*Math.sin(angle)); ctx.stroke();
    ctx.fillStyle = 'var(--danger)'; ctx.beginPath(); ctx.arc(pivot-100*Math.cos(angle), 150+100*Math.sin(angle), 15, 0, Math.PI*2); ctx.fill();
    ctx.fillStyle = 'var(--success)'; ctx.beginPath(); ctx.arc(pivot+L2*0.7*Math.cos(angle), 150-L2*0.7*Math.sin(angle), 12, 0, Math.PI*2); ctx.fill();
    ctx.fillStyle = 'var(--text)'; ctx.font = '12px monospace';
    ctx.fillText('动力', pivot-130, 120); ctx.fillText('阻力', pivot+L2*0.5, 120);
    requestAnimationFrame(draw);
  }
  draw();
})();
</script>''',
        '''<h3>🧪 实验 2：滑轮组省力分析</h3>
<div class="demo-box">
  <canvas id="pulleyCanvas" width="500" height="250"></canvas>
  <div style="margin-top:10px">
    <button class="btn" onclick="setPulley(1)">1 段绳子</button>
    <button class="btn btn-ghost" onclick="setPulley(2)">2 段绳子</button>
    <button class="btn btn-ghost" onclick="setPulley(3)">3 段绳子</button>
  </div>
  <p style="font-size:12px;color:var(--text-dim);margin-top:8px">选择不同滑轮组，观察拉力变化。F = G/n</p>
</div>
<script>
(function(){
  const c = document.getElementById('pulleyCanvas'); if(!c) return;
  const ctx = c.getContext('2d');
  let n = 1;
  window.setPulley = function(nv) { n = nv; };
  function draw() {
    ctx.clearRect(0,0,500,250);
    ctx.fillStyle = 'var(--panel)'; ctx.fillRect(150, 50, 200, 20);
    ctx.fillStyle = 'var(--accent)'; ctx.beginPath(); ctx.arc(200, 100, 25, 0, Math.PI*2); ctx.fill();
    if(n > 1) { ctx.beginPath(); ctx.arc(300, 100, 25, 0, Math.PI*2); ctx.fill(); }
    if(n > 2) { ctx.beginPath(); ctx.arc(250, 150, 25, 0, Math.PI*2); ctx.fill(); }
    ctx.strokeStyle = 'var(--text)'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(200, 125); ctx.lineTo(200, 200); ctx.stroke();
    ctx.fillStyle = 'var(--danger)'; ctx.fillRect(180, 200, 40, 30);
    ctx.fillStyle = 'var(--text)'; ctx.font = '14px monospace';
    ctx.fillText('G', 200, 250); ctx.fillText('F = G/' + n, 350, 100);
    requestAnimationFrame(draw);
  }
  draw();
})();
</script>''',
    ],
}

def process_ch78(ch_dir, ch_key):
    path = os.path.join(BASE, ch_dir, 'tutorial.html')
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Match top-level sections: <section id="sec-xxx">
    pattern = r'(<section\s+id="sec-[^"]+"[^>]*>)'
    starts = list(re.finditer(pattern, text))
    
    if not starts:
        print(f"  {ch_dir}: no sec- sections found")
        return False
    
    print(f"  {ch_dir}: {len(starts)} sections found")
    
    new_text = text[:starts[0].start()]
    for i, m in enumerate(starts):
        start = m.start()
        end = starts[i+1].start() if i+1 < len(starts) else len(text)
        unit_html = text[start:end]
        
        has_ex = len(re.findall(r'例题', unit_html)) >= 3
        has_quiz = len(re.findall(r'quiz-option|quiz-btn', unit_html)) >= 5
        has_svg = len(re.findall(r'<canvas|<svg', unit_html)) >= 2
        
        additions = []
        
        if not has_svg and ch_key in SVG_TEMPLATES:
            svgs = SVG_TEMPLATES[ch_key]
            idx = (i * 2) % len(svgs)
            additions.append(svgs[idx])
            if idx + 1 < len(svgs):
                additions.append(svgs[idx+1])
        
        if not has_ex and i < len(starts) - 1:
            for n in range(1, 4):
                additions.append(EXAMPLE_HTML.replace('{n}', str(n)))
        
        if not has_quiz:
            for n in range(1, 6):
                additions.append(QUIZ_HTML.replace('{u}', str(i)).replace('{n}', str(n)))
        
        if additions:
            # Insert before </section>
            last_close = unit_html.rfind('</section>')
            if last_close == -1:
                unit_html += '\n' + '\n'.join(additions)
            else:
                unit_html = unit_html[:last_close] + '\n' + '\n'.join(additions) + '\n' + unit_html[last_close:]
        
        new_text += unit_html
    
    new_text += text[starts[-1].end():] if starts else ''
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    
    return True

for ch_dir, ch_key in [('grade8-sem2-ch07','ch07'), ('grade8-sem2-ch08','ch08')]:
    try:
        ok = process_ch78(ch_dir, ch_key)
        if not ok:
            print(f"  {ch_dir}: FAILED")
    except Exception as e:
        print(f"  {ch_dir}: ERROR - {e}")

print("\nDone.")
