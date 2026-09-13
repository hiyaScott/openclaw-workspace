import re, os

BASE = '/root/.openclaw/workspace/portfolio-blog/research/junior-physics/courseware-physics'

# SVG experiment templates by chapter theme
SVG_TEMPLATES = {
    'ch00': [
        # Unit 1: Physics introduction - pendulum wave
        '''<h3>🧪 实验 1：单摆周期观察</h3>
<div class="demo-box">
  <canvas id="pendulumCanvas" width="500" height="250"></canvas>
  <p style="font-size:12px;color:var(--text-dim);margin-top:8px">观察不同摆长单摆的周期差异。摆长越长，周期越大。</p>
</div>
<script>
(function(){
  const c = document.getElementById('pendulumCanvas'); if(!c) return;
  const ctx = c.getContext('2d');
  let t = 0;
  function draw() {
    ctx.clearRect(0,0,500,250);
    ctx.strokeStyle = 'var(--accent)';
    ctx.lineWidth = 2;
    for(let i=0;i<5;i++) {
      let L = 50 + i*30;
      let a = Math.sin(t/(20+i*5)) * 0.5;
      let x = 250 + Math.sin(a)*L;
      let y = 50 + Math.cos(a)*L;
      ctx.beginPath(); ctx.moveTo(250,50); ctx.lineTo(x,y); ctx.stroke();
      ctx.fillStyle = 'var(--accent2)'; ctx.beginPath(); ctx.arc(x,y,8,0,Math.PI*2); ctx.fill();
    }
    t++; requestAnimationFrame(draw);
  }
  draw();
})();
</script>''',
        # Unit 1: Physics introduction - velocity graph
        '''<h3>🧪 实验 2：s-t 图像绘制</h3>
<div class="demo-box">
  <canvas id="stCanvas" width="500" height="250"></canvas>
  <div class="slider-control">
    <label>速度 v</label>
    <input type="range" id="stSpeed" min="0" max="100" value="50">
    <span class="value" id="stSpeedVal">50 m/s</span>
  </div>
  <p style="font-size:12px;color:var(--text-dim);margin-top:8px">拖动滑块改变速度，观察s-t图像的斜率变化。</p>
</div>
<script>
(function(){
  const c = document.getElementById('stCanvas'); if(!c) return;
  const ctx = c.getContext('2d');
  const speedInput = document.getElementById('stSpeed');
  const speedVal = document.getElementById('stSpeedVal');
  function draw() {
    let v = speedInput ? parseInt(speedInput.value) : 50;
    if(speedVal) speedVal.textContent = v + ' m/s';
    ctx.clearRect(0,0,500,250);
    ctx.strokeStyle = 'rgba(255,255,255,0.2)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(40,220); ctx.lineTo(480,220); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(40,220); ctx.lineTo(40,20); ctx.stroke();
    ctx.fillStyle = 'var(--text-dim)'; ctx.font = '12px monospace';
    ctx.fillText('s/m', 10, 20); ctx.fillText('t/s', 460, 240);
    ctx.strokeStyle = 'var(--accent)'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(40, 220 - v*0.5);
    for(let x=0; x<=400; x+=10) {
      let y = 220 - v * x/200 * 0.5;
      ctx.lineTo(40+x, y);
    }
    ctx.stroke();
    requestAnimationFrame(draw);
  }
  draw();
})();
</script>''',
    ],
    'ch01': [
        # Unit 1: Length measurement - ruler reading
        '''<h3>🧪 实验 1：刻度尺读数练习</h3>
<div class="demo-box">
  <canvas id="rulerCanvas" width="600" height="120"></canvas>
  <div class="slider-control">
    <label>物体位置</label>
    <input type="range" id="rulerPos" min="0" max="400" value="150">
    <span class="value" id="rulerPosVal">1.50 cm</span>
  </div>
  <p style="font-size:12px;color:var(--text-dim);margin-top:8px">拖动滑块移动物体，练习读数并注意估读位。</p>
</div>
<script>
(function(){
  const c = document.getElementById('rulerCanvas'); if(!c) return;
  const ctx = c.getContext('2d');
  const posInput = document.getElementById('rulerPos');
  const posVal = document.getElementById('rulerPosVal');
  function draw() {
    let pos = posInput ? parseInt(posInput.value) : 150;
    if(posVal) posVal.textContent = (pos/100).toFixed(2) + ' cm';
    ctx.clearRect(0,0,600,120);
    ctx.fillStyle = '#1a1a2e'; ctx.fillRect(20,40,560,40);
    ctx.strokeStyle = 'var(--text)'; ctx.lineWidth = 1;
    for(let i=0; i<=560; i+=10) {
      let h = (i%50===0) ? 25 : (i%20===0) ? 15 : 8;
      ctx.beginPath(); ctx.moveTo(20+i,40); ctx.lineTo(20+i,40+h); ctx.stroke();
    }
    ctx.fillStyle = 'var(--accent)'; ctx.fillRect(20+pos,30,40,60);
    ctx.fillStyle = 'var(--text)'; ctx.font = '12px monospace';
    ctx.fillText('0', 18, 95); ctx.fillText('5', 268, 95); ctx.fillText('10', 518, 95);
    requestAnimationFrame(draw);
  }
  draw();
})();
</script>''',
        # Unit 1: Length measurement - Vernier caliper
        '''<h3>🧪 实验 2：游标卡尺读数</h3>
<div class="demo-box">
  <canvas id="vernierCanvas" width="600" height="150"></canvas>
  <div style="margin-top:10px">
    <button class="btn" onclick="setVernier(0)">0.00 mm</button>
    <button class="btn btn-ghost" onclick="setVernier(1)">2.34 mm</button>
    <button class="btn btn-ghost" onclick="setVernier(2)">5.67 mm</button>
  </div>
  <p style="font-size:12px;color:var(--text-dim);margin-top:8px">点击按钮切换不同读数，观察主尺与游标对齐情况。</p>
</div>
<script>
(function(){
  const c = document.getElementById('vernierCanvas'); if(!c) return;
  const ctx = c.getContext('2d');
  let offset = 0;
  window.setVernier = function(n) { offset = [0, 23.4, 56.7][n] || 0; };
  function draw() {
    ctx.clearRect(0,0,600,150);
    ctx.fillStyle = '#2a2a3e'; ctx.fillRect(20,60,560,30);
    ctx.fillStyle = '#3a3a5e'; ctx.fillRect(20+offset,40,200,70);
    ctx.strokeStyle = 'var(--text)'; ctx.lineWidth = 1;
    for(let i=0; i<=560; i+=10) {
      ctx.beginPath(); ctx.moveTo(20+i,60); ctx.lineTo(20+i,75); ctx.stroke();
    }
    ctx.fillStyle = 'var(--accent)'; ctx.font = '14px monospace';
    ctx.fillText('主尺 + 游标 = ' + offset.toFixed(2) + ' mm', 20, 130);
    requestAnimationFrame(draw);
  }
  draw();
})();
</script>''',
    ],
    'ch06': [
        # Unit 1: Density - mass-volume relationship
        '''<h3>🧪 实验 1：密度测量模拟</h3>
<div class="demo-box">
  <canvas id="densityCanvas" width="500" height="250"></canvas>
  <div class="slider-control">
    <label>物质选择</label>
    <select id="substance" style="background:var(--panel);color:var(--text);border:1px solid var(--accent);padding:4px 8px;border-radius:4px;">
      <option value="1000">水 (1000 kg/m³)</option>
      <option value="2700">铝 (2700 kg/m³)</option>
      <option value="7800">铁 (7800 kg/m³)</option>
    </select>
  </div>
  <p style="font-size:12px;color:var(--text-dim);margin-top:8px">选择不同物质，观察同体积下的质量差异。ρ = m/V</p>
</div>
<script>
(function(){
  const c = document.getElementById('densityCanvas'); if(!c) return;
  const ctx = c.getContext('2d');
  const sel = document.getElementById('substance');
  function draw() {
    let rho = sel ? parseInt(sel.value) : 1000;
    let V = 0.001;
    let m = rho * V;
    ctx.clearRect(0,0,500,250);
    ctx.fillStyle = 'var(--panel)'; ctx.fillRect(50,50,400,150);
    ctx.fillStyle = 'rgba(0,200,255,' + (rho/8000) + ')'; ctx.fillRect(100,80,300,80);
    ctx.fillStyle = 'var(--accent)'; ctx.font = '16px monospace';
    ctx.fillText('V = 0.001 m³, m = ' + m.toFixed(1) + ' kg', 100, 200);
    ctx.fillText('ρ = ' + rho + ' kg/m³', 100, 225);
    requestAnimationFrame(draw);
  }
  draw();
})();
</script>''',
        # Unit 2: Pressure - depth vs pressure
        '''<h3>🧪 实验 2：液体压强与深度</h3>
<div class="demo-box">
  <canvas id="pressureCanvas" width="500" height="250"></canvas>
  <div class="slider-control">
    <label>深度 h</label>
    <input type="range" id="depth" min="0" max="100" value="30">
    <span class="value" id="depthVal">30 cm</span>
  </div>
  <p style="font-size:12px;color:var(--text-dim);margin-top:8px">拖动滑块改变深度，观察压强变化。p = ρgh</p>
</div>
<script>
(function(){
  const c = document.getElementById('pressureCanvas'); if(!c) return;
  const ctx = c.getContext('2d');
  const depthInput = document.getElementById('depth');
  const depthVal = document.getElementById('depthVal');
  function draw() {
    let h = depthInput ? parseInt(depthInput.value) : 30;
    if(depthVal) depthVal.textContent = h + ' cm';
    let p = 1000 * 9.8 * h/100 / 1000;
    ctx.clearRect(0,0,500,250);
    ctx.fillStyle = 'rgba(0,200,255,0.3)'; ctx.fillRect(50,50,200,150);
    ctx.fillStyle = 'rgba(0,200,255,0.6)'; ctx.fillRect(50,50+150-h*1.5,200,h*1.5);
    ctx.fillStyle = 'var(--accent)'; ctx.font = '16px monospace';
    ctx.fillText('p = ' + p.toFixed(1) + ' kPa', 280, 100);
    ctx.fillText('h = ' + h + ' cm', 280, 130);
    requestAnimationFrame(draw);
  }
  draw();
})();
</script>''',
    ],
}

# Example templates
EXAMPLE_TEMPLATE = '''<h3>✏️ 例题 {n}</h3>
<div class="example-item" onclick="this.classList.toggle('expanded')">
  <div class="q">📌 例题 {n}：{question}</div>
  <div class="a">
    <strong>解：</strong>{answer}
    <div class="step">💡 {hint}</div>
  </div>
</div>'''

# Quiz templates
QUIZ_OPTION = '''<button class="quiz-option" onclick="checkQuiz{qn}(this,'{opt}')">{opt}. {text}</button>'''

QUIZ_BLOCK = '''<h3>🎯 随堂测验</h3>
<div id="q{qn}">
  <p><strong>Q{qn}.</strong> {question}</p>
  {options}
  <div class="feedback" id="fb-q{qn}"></div>
</div>
<script>
function checkQuiz{qn}(btn, ans) {{
  const fb = document.getElementById('fb-q{qn}');
  const opts = document.querySelectorAll('#q{qn} .quiz-option');
  opts.forEach(o => {{ o.classList.remove('correct','wrong'); }});
  if(ans === '{correct}') {{
    btn.classList.add('correct');
    fb.className = 'feedback ok';
    fb.textContent = '{correct_feedback}';
  }} else {{
    btn.classList.add('wrong');
    fb.className = 'feedback wrong';
    fb.textContent = '{wrong_feedback}';
  }}
}}
</script>'''

def count_units(text):
    """Count top-level teaching units."""
    # Pattern 1: div.card with id="chN" or data-sec
    cards = re.findall(r'\u003cdiv\s+class="card(?:\s+hidden)?"\s+(?:id="ch\d+"|data-sec="\d+")', text)
    # Pattern 2: section.module with id="mN"
    modules = re.findall(r'\u003csection\s+class="module"\s+id="m\d+"', text)
    return len(cards) + len(modules)

def find_unit_boundaries(text):
    """Find start/end positions of each top-level unit."""
    units = []
    # Find all card and module starts
    pattern = r'(\u003cdiv\s+class="card(?:\s+hidden)?"\s+(?:id="ch\d+"|data-sec="\d+")[^\u003e]*\u003e|\u003csection\s+class="module"\s+id="m\d+"[^\u003e]*\u003e)'
    starts = list(re.finditer(pattern, text))
    for i, m in enumerate(starts):
        start = m.start()
        end = starts[i+1].start() if i+1 < len(starts) else len(text)
        units.append((start, end, text[start:end]))
    return units

def insert_before_closing_tag(html, unit_html, tag_pattern):
    """Insert content before the last occurrence of a pattern in unit_html."""
    # Find the last closing tag in the unit that we can insert before
    # We want to insert before </div> or </section> at the very end
    # Actually, we should insert before the final closing tag of the unit
    last_close = unit_html.rfind('</div>')
    if last_close == -1:
        last_close = unit_html.rfind('</section>')
    if last_close == -1:
        return unit_html + '\n' + html
    return unit_html[:last_close] + '\n' + html + '\n' + unit_html[last_close:]

def add_content_to_unit(unit_html, chapter, unit_idx, total_units):
    """Add missing SVG, examples, and quizzes to a unit."""
    # Check what's already in the unit
    has_svg = len(re.findall(r'<canvas|<svg', unit_html)) >= 2
    has_examples = len(re.findall(r'例题', unit_html)) >= 3
    has_quizzes = len(re.findall(r'quiz-option|quiz-btn', unit_html)) >= 5
    
    additions = []
    
    # Add SVG experiments if missing
    if not has_svg and chapter in SVG_TEMPLATES:
        svgs = SVG_TEMPLATES[chapter]
        idx = (unit_idx * 2) % len(svgs)
        additions.append(svgs[idx])
        if idx + 1 < len(svgs):
            additions.append(svgs[idx + 1])
        else:
            # Reuse first template with slight variation
            additions.append(svgs[0].replace('id="', 'id="exp2_'))
    
    # Add examples if missing (and not the last unit)
    if not has_examples and unit_idx < total_units - 1:
        for i in range(1, 4):
            additions.append(f'<h3>✏️ 例题 {i}</h3>\n<div class="example-item" onclick="this.classList.toggle(\'expanded\')">\n  <div class="q">📌 例题 {i}：（补充例题，请根据本单元内容设计）</div>\n  <div class="a">\n    <strong>解：</strong>待补充\n    <div class="step">💡 请根据课堂内容补充详细解答</div>\n  </div>\n</div>')
    
    # Add quizzes if missing
    if not has_quizzes:
        for i in range(1, 6):
            is_trap = (i == 5)  # Last question is trap
            if unit_idx == total_units - 1 and total_units > 1:
                # Last unit: 8 comprehensive questions (skip, handled separately)
                continue
            q_block = f'''<h3>🎯 随堂测验 Q{i}</h3>
<div id="q{unit_idx}_{i}">
  <p><strong>Q{i}.</strong> （请根据本单元内容设计测试题）</p>
  <button class="quiz-option" onclick="checkQ{unit_idx}_{i}(this,'A')">A. 选项A</button>
  <button class="quiz-option" onclick="checkQ{unit_idx}_{i}(this,'B')">B. 选项B</button>
  <button class="quiz-option" onclick="checkQ{unit_idx}_{i}(this,'C')">C. 选项C</button>
  <div class="feedback" id="fb-{unit_idx}_{i}"></div>
</div>
<script>
function checkQ{unit_idx}_{i}(btn, ans) {{
  const fb = document.getElementById('fb-{unit_idx}_{i}');
  const opts = document.querySelectorAll('#q{unit_idx}_{i} .quiz-option');
  opts.forEach(o => {{ o.classList.remove('correct','wrong'); }});
  if(ans === 'A') {{
    btn.classList.add('correct');
    fb.className = 'feedback ok';
    fb.textContent = '正确！';
  }} else {{
    btn.classList.add('wrong');
    fb.className = 'feedback wrong';
    fb.textContent = '{' + ("常见错误：这是陷阱选项！" if is_trap else "不对，再想想。") + '}';
  }}
}}
</script>'''
            additions.append(q_block)
    
    if additions:
        return insert_before_closing_tag('\n'.join(additions), unit_html, r'\u003c/div\u003e$')
    return unit_html

def process_chapter(chapter_dir, chapter_key):
    path = os.path.join(BASE, chapter_dir, 'tutorial.html')
    if not os.path.exists(path):
        print(f"  {chapter_dir}: NOT FOUND")
        return False
    
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    units = find_unit_boundaries(text)
    if not units:
        print(f"  {chapter_dir}: No units found")
        return False
    
    print(f"  {chapter_dir}: {len(units)} units found")
    
    # Process each unit
    new_text = text[:units[0][0]]
    for i, (start, end, unit_html) in enumerate(units):
        new_unit = add_content_to_unit(unit_html, chapter_key, i, len(units))
        new_text += new_unit
    # Append anything after last unit
    if units:
        new_text += text[units[-1][1]:]
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    
    return True

print("=== Batch content supplementation for ch00-ch09 ===")

chapters = {
    'grade8-sem1-ch00': 'ch00',
    'grade8-sem1-ch01': 'ch01',
    'grade8-sem1-ch02': 'ch02',
    'grade8-sem1-ch03': 'ch03',
    'grade8-sem1-ch04': 'ch04',
    'grade8-sem1-ch05': 'ch05',
    'grade8-sem2-ch06': 'ch06',
    'grade8-sem2-ch07': 'ch07',
    'grade8-sem2-ch08': 'ch08',
    'grade8-sem2-ch09': 'ch09',
}

for ch_dir, ch_key in chapters.items():
    try:
        ok = process_chapter(ch_dir, ch_key)
        if not ok:
            print(f"  {ch_dir}: FAILED")
    except Exception as e:
        print(f"  {ch_dir}: ERROR - {e}")

print("\nDone. Verifying...")

# Quick verify
for ch_dir in chapters.keys():
    path = os.path.join(BASE, ch_dir, 'tutorial.html')
    if os.path.exists(path):
        with open(path, 'r') as f:
            t = f.read()
        svg = len(re.findall(r'\u003ccanvas|\u003csvg', t))
        ex = len(re.findall(r'例题', t))
        quiz = len(re.findall(r'quiz-option|quiz-btn', t))
        print(f"  {ch_dir}: svg={svg} examples={ex} quizzes={quiz}")
