/**
 * C++ 课程网站 - 核心逻辑
 * 支持：课程列表渲染、筛选、详情页加载、上下课导航
 */

(function () {
  'use strict';

  // ===== 状态 =====
  let coursesData = { courses: [] };
  let currentCourseId = null;

  // ===== 工具函数 =====
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  function getParam(name) {
    return new URLSearchParams(location.search).get(name);
  }

  // ===== 加载课程数据 =====
  async function loadCourses() {
    try {
      const res = await fetch('data/courses.json');
      if (!res.ok) throw new Error('加载失败');
      coursesData = await res.json();
      return coursesData;
    } catch (e) {
      console.error('课程数据加载失败:', e);
      return { courses: [] };
    }
  }

  // ===== 首页：渲染课程列表（按部分分组）=====
  function renderCourseList(filterLevel = 'all') {
    const container = $('#courseGroups');
    if (!container) return;

    const courses = coursesData.courses || [];
    const filtered = filterLevel === 'all'
      ? courses
      : courses.filter(c => c.level === filterLevel);

    if (filtered.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <p>暂无该分类的课程</p>
        </div>
      `;
      return;
    }

    // 按 part 分组
    const groups = {};
    filtered.forEach(c => {
      const part = c.part || '未分类';
      if (!groups[part]) groups[part] = [];
      groups[part].push(c);
    });

    // 保持原始顺序
    const orderedParts = [];
    courses.forEach(c => {
      if (!orderedParts.includes(c.part)) orderedParts.push(c.part);
    });

    container.innerHTML = orderedParts
      .filter(part => groups[part] && groups[part].length > 0)
      .map(part => `
        <section class="course-group">
          <h3 class="group-title">${escapeHtml(part)}</h3>
          <div class="course-grid">
            ${groups[part].map(c => renderCard(c)).join('')}
          </div>
        </section>
      `).join('');
  }

  // ===== 学习状态管理 =====
  function getProgress() {
    try {
      return JSON.parse(localStorage.getItem('cpp_progress') || '{}');
    } catch (e) {
      return {};
    }
  }

  function saveProgress(progress) {
    localStorage.setItem('cpp_progress', JSON.stringify(progress));
  }

  function getCourseProgress(courseId) {
    return getProgress()[courseId] || 'not_started';
  }

  function setCourseProgress(courseId, status) {
    const progress = getProgress();
    progress[courseId] = status;
    saveProgress(progress);
  }

  // ===== 二次确认对话框 =====
  let confirmCallback = null;

  function showConfirmDialog(title, message, onConfirm) {
    const dialog = $('#confirmDialog');
    const titleEl = $('#confirmDialogTitle');
    const msgEl = $('#confirmDialogMessage');
    const confirmBtn = $('#confirmDialogConfirmBtn');

    if (!dialog || !titleEl || !msgEl || !confirmBtn) return;

    titleEl.textContent = title;
    msgEl.textContent = message;
    confirmCallback = onConfirm;

    // 移除旧事件，绑定新事件
    const newBtn = confirmBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newBtn, confirmBtn);
    newBtn.addEventListener('click', () => {
      closeConfirmDialog();
      if (confirmCallback) confirmCallback();
    });

    dialog.style.display = 'block';
    document.body.style.overflow = 'hidden';
  }

  window.closeConfirmDialog = function () {
    const dialog = $('#confirmDialog');
    if (dialog) dialog.style.display = 'none';
    document.body.style.overflow = '';
    confirmCallback = null;
  };

  // ===== 切换学习状态 =====
  window.toggleProgress = function () {
    if (!currentCourseId) return;

    const current = getCourseProgress(currentCourseId);

    if (current === 'completed') {
      // 取消完成 — 需要确认
      showConfirmDialog(
        '取消完成标记',
        '确定要将该课程标记为"未开始"吗？此操作会重置学习进度。',
        () => {
          setCourseProgress(currentCourseId, 'not_started');
          updateProgressUI();
        }
      );
    } else {
      // 标记完成 — 需要确认
      showConfirmDialog(
        '确认完成',
        '确定要将该课程标记为"已完成"吗？',
        () => {
          setCourseProgress(currentCourseId, 'completed');
          updateProgressUI();
        }
      );
    }
  };

  function updateProgressUI() {
    if (!currentCourseId) return;

    const status = getCourseProgress(currentCourseId);
    const statusEl = $('#progressStatus');
    const btn = $('#progressBtn');

    if (!statusEl || !btn) return;

    if (status === 'completed') {
      statusEl.textContent = '✅ 已完成';
      statusEl.className = 'progress-status status-completed';
      btn.textContent = '取消完成标记';
      btn.className = 'progress-btn btn-secondary';
    } else {
      statusEl.textContent = '○ 未开始';
      statusEl.className = 'progress-status status-not-started';
      btn.textContent = '标记为已完成';
      btn.className = 'progress-btn btn-primary';
    }
  }

  // ===== 首页：渲染课程卡片（带进度）=====
  function renderCard(c) {
    const externalBadge = c.external_video
      ? `<span class="external-badge">🔗 外部视频</span>`
      : '';

    const progress = getCourseProgress(c.id);
    const progressBadge = progress === 'completed'
      ? `<span class="progress-badge">✅</span>`
      : '';

    return `
      <article class="course-card" data-id="${c.id}" onclick="goToCourse('${c.id}')">
        <div class="card-thumbnail">
          <div class="play-icon">▶</div>
          ${externalBadge}
          ${progressBadge}
          <span class="duration">${c.duration}</span>
        </div>
        <div class="card-body">
          <h3 class="card-title">${escapeHtml(c.title)}</h3>
          <p class="card-desc">${escapeHtml(c.description)}</p>
          <div class="card-footer">
            <span class="level-badge" data-level="${c.level}">${c.level}</span>
            <div class="card-tags">
              ${(c.tags || []).map(t => `<span>${escapeHtml(t)}</span>`).join('')}
            </div>
          </div>
        </div>
      </article>
    `;
  }

  // ===== 首页：筛选标签事件 =====
  function initFilters() {
    const tabs = $$('.filter-tabs .tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        renderCourseList(tab.dataset.filter);
      });
    });
  }

  // ===== 详情页：加载课程 =====
  function loadCourseDetail(courseId) {
    const courses = coursesData.courses || [];
    const course = courses.find(c => c.id === courseId);
    if (!course) {
      showNotFound();
      return;
    }

    currentCourseId = courseId;

    // 更新标题
    document.title = `${course.title} - C++ 核心课程`;
    const navTitle = $('#navTitle');
    if (navTitle) navTitle.textContent = course.title;

    // 更新课程信息（右侧栏）
    const titleEl = $('#courseTitle');
    if (titleEl) titleEl.textContent = course.title;

    const levelEl = $('#courseLevel');
    if (levelEl) {
      levelEl.textContent = course.level;
      levelEl.dataset.level = course.level;
    }

    const durEl = $('#courseDuration');
    if (durEl) durEl.textContent = course.duration;

    const descEl = $('#courseDesc');
    if (descEl) descEl.textContent = course.description;

    const tagsEl = $('#courseTags');
    if (tagsEl) {
      tagsEl.innerHTML = (course.tags || []).map(t =>
        `<span>${escapeHtml(t)}</span>`
      ).join('');
    }

    // 更新视频卡片
    const videoCard = $('#videoCard');
    const videoLink = $('#videoLink');
    const videoNote = $('#videoCardNote');

    if (course.external_video) {
      if (videoCard) videoCard.style.display = 'flex';
      if (videoLink) videoLink.href = course.external_video;
      if (videoNote) videoNote.textContent = course.external_note || '点击跳转到视频平台观看';
    } else {
      if (videoCard) videoCard.style.display = 'none';
    }

    // 更新腾讯会议卡片
    const tencentCard = $('#tencentCard');
    const tencentLink = $('#tencentLink');
    const tencentNote = $('#tencentCardNote');
    const resourceTags = $('#resourceTags');

    if (course.tencent_meeting) {
      if (tencentCard) tencentCard.style.display = 'flex';
      if (tencentLink) tencentLink.href = course.tencent_meeting;
      if (tencentNote) tencentNote.textContent = course.tencent_note || '腾讯会议录制';
      if (resourceTags) resourceTags.style.display = 'flex';
    } else {
      if (tencentCard) tencentCard.style.display = 'none';
      if (resourceTags) resourceTags.style.display = 'none';
    }

    // 加载课程纪要
    loadMeetingNotes(courseId);

    // 渲染练习题
    renderExercises(course);

    // 更新学习状态UI
    updateProgressUI();

    // 更新 PDF（左侧主体）
    const pdfFrame = $('#pdfFrame');
    if (pdfFrame) pdfFrame.src = course.pdf;

    const pdfDownload = $('#pdfDownload');
    if (pdfDownload) pdfDownload.href = course.pdf;

    // 渲染导航
    renderLessonNav(courseId, courses);
  }

  // ===== 渲染练习题 =====
  function renderExercises(course) {
    const section = $('#exercisesSection');
    const container = $('#exercisesGroups');
    if (!section || !container) return;

    const ex = course.exercises;
    if (!ex || (!ex.basic && !ex.practice && !ex.advanced)) {
      section.style.display = 'none';
      return;
    }

    section.style.display = 'block';

    const groups = [
      { key: 'basic', label: '⭐ 基础练习', desc: '直接应用课堂知识点' },
      { key: 'practice', label: '⭐⭐ 巩固提升', desc: '需要组合多个知识点' },
      { key: 'advanced', label: '⭐⭐⭐ 挑战拓展', desc: '灵活运用，需要思考' }
    ];

    container.innerHTML = groups.map(g => {
      const items = ex[g.key] || [];
      if (items.length === 0) return '';
      return `
        <div class="exercise-group">
          <div class="exercise-group-header">
            <span class="exercise-group-label">${g.label}</span>
            <span class="exercise-group-desc">${g.desc}</span>
          </div>
          <div class="exercise-list">
            ${items.map(item => `
              <a href="${escapeHtml(item.url)}" target="_blank" rel="noopener" class="exercise-item">
                <span class="exercise-id">${escapeHtml(item.id)}</span>
                <span class="exercise-name">${escapeHtml(item.title)}</span>
                <span class="exercise-arrow">→</span>
              </a>
            `).join('')}
          </div>
        </div>
      `;
    }).join('');
  }

  // ===== 加载课程纪要 =====
  async function loadMeetingNotes(courseId) {
    const notesContainer = $('#meetingNotes');
    if (!notesContainer) return;

    try {
      const res = await fetch('data/meeting-notes.json');
      if (!res.ok) return;
      const notesData = await res.json();
      const notes = notesData[courseId];
      if (!notes) {
        notesContainer.style.display = 'none';
        return;
      }

      notesContainer.style.display = 'block';

      const sourceEl = $('#notesSource');
      if (sourceEl) sourceEl.textContent = `来源：${notes.source} · ${notes.url}`;

      const summaryEl = $('#notesSummary');
      if (summaryEl) summaryEl.textContent = notes.summary;

      const sectionsEl = $('#notesSections');
      if (sectionsEl) {
        sectionsEl.innerHTML = (notes.sections || []).map(section => `
          <div class="notes-section">
            <div class="notes-section-title">
              ${escapeHtml(section.title)}
              <span class="notes-section-time">${escapeHtml(section.time)}</span>
            </div>
            ${(section.items || []).map(item => `
              <div class="notes-item">
                <div class="notes-item-subtitle">${escapeHtml(item.subtitle)}</div>
                <div class="notes-item-content">${escapeHtml(item.content)}</div>
              </div>
            `).join('')}
          </div>
        `).join('');
      }

      // 绑定展开/收起
      const toggle = $('#notesToggle');
      if (toggle) {
        toggle.addEventListener('click', () => {
          notesContainer.classList.toggle('open');
          const content = $('#notesContent');
          if (content) {
            content.style.display = notesContainer.classList.contains('open') ? 'block' : 'none';
          }
        });
      }
    } catch (e) {
      console.error('纪要加载失败:', e);
      notesContainer.style.display = 'none';
    }
  }

  // ===== 详情页：上下课导航 =====
  function renderLessonNav(currentId, courses) {
    const nav = $('#lessonNav');
    if (!nav) return;

    const idx = courses.findIndex(c => c.id === currentId);
    const prev = idx > 0 ? courses[idx - 1] : null;
    const next = idx < courses.length - 1 ? courses[idx + 1] : null;
    const currentNum = idx + 1;
    const total = courses.length;

    nav.innerHTML = `
      <button class="lesson-nav-btn" onclick="goToCourse('${prev ? prev.id : ''}')" ${!prev ? 'disabled' : ''}>
        <span>←</span>
        <div>
          <div class="label">上一课</div>
          <div class="title">${prev ? escapeHtml(prev.title) : '没有了'}</div>
        </div>
      </button>

      <span class="lesson-nav-center">${currentNum} / ${total}</span>

      <button class="lesson-nav-btn" onclick="goToCourse('${next ? next.id : ''}')" ${!next ? 'disabled' : ''}>
        <div style="text-align: right;">
          <div class="label">下一课</div>
          <div class="title">${next ? escapeHtml(next.title) : '没有了'}</div>
        </div>
        <span>→</span>
      </button>
    `;
  }

  // ===== 404 =====
  function showNotFound() {
    const main = $('.course-main');
    if (main) {
      main.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1; padding-top: 120px;">
          <h2 style="margin-bottom: 12px;">课程未找到</h2>
          <p>该课程不存在或已被移除</p>
          <br>
          <a href="index.html" style="color: var(--accent);">← 返回课程列表</a>
        </div>
      `;
    }
  }

  // ===== HTML 转义 =====
  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // ===== 全局跳转 =====
  window.goToCourse = function (id) {
    if (!id) return;
    location.href = `course.html?id=${id}`;
  };

  // ===== 主题切换 =====
  function initTheme() {
    const saved = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = saved || (prefersDark ? 'dark' : 'light');
    setTheme(theme);
  }

  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    const btn = $('#themeToggle');
    if (btn) btn.textContent = theme === 'dark' ? '🌙' : '☀️';
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    setTheme(current === 'dark' ? 'light' : 'dark');
  }

  // ===== 初始化 =====
  async function init() {
    initTheme();

    const themeBtn = $('#themeToggle');
    if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

    await loadCourses();

    const page = location.pathname.split('/').pop();

    if (page === 'index.html' || page === '' || page === '/') {
      // 首页
      renderCourseList();
      initFilters();
    } else if (page === 'course.html') {
      // 详情页
      const id = getParam('id');
      if (id) {
        loadCourseDetail(id);
      } else {
        showNotFound();
      }
    }
  }

  // DOM 就绪后启动
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
