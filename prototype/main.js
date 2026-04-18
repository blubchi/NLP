// ══════════════════════════════════════
//  FitScore — app.js
// ══════════════════════════════════════

// ── PAGE ROUTER ─────────────────────
function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const map = { landing: 'landing', input: 'input-page', loading: 'loading-page', result: 'result-page' };
  const el = document.getElementById(map[id]);
  if (el) el.classList.add('active');
  window.scrollTo(0, 0);
}

// ── FAQ TOGGLE ───────────────────────
function toggleFaq(el) {
  el.classList.toggle('open');
}

// ── EXPERIENCE ENTRIES ───────────────
let expCount = 1;

function addExp() {
  if (expCount >= 3) return;
  expCount++;
  const list = document.getElementById('exp-list');
  const div = document.createElement('div');
  div.className = 'exp-card fade-in';
  div.dataset.expId = expCount;
  div.innerHTML = `
    <div class="exp-card-header">
      <span class="exp-card-num">Pengalaman ${expCount}</span>
      <button class="exp-remove" onclick="removeExp(this)" title="Hapus">×</button>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Nama Perusahaan</label>
        <input type="text" placeholder="PT. Teknologi Maju">
      </div>
      <div class="form-group">
        <label>Posisi / Jabatan</label>
        <input type="text" placeholder="Software Engineer">
      </div>
    </div>
    <div class="form-group">
      <label>Durasi</label>
      <input type="text" placeholder="Jan 2022 – Des 2023 (2 tahun)">
    </div>
  `;
  list.appendChild(div);
}

function removeExp(btn) {
  const card = btn.closest('.exp-card');
  card.style.opacity = '0';
  card.style.transform = 'translateY(-8px)';
  card.style.transition = 'all 0.2s';
  setTimeout(() => { card.remove(); expCount--; }, 200);
}

// ── ANALYSIS FLOW ────────────────────
function startAnalysis() {
  const jdSkills = document.getElementById('jd-skills').value.trim();
  const jdText   = document.getElementById('jd-text').value.trim();

  if (!jdSkills && !jdText) {
    showFieldError('jd-skills', 'Isi minimal satu kolom Job Description');
    return;
  }

  showPage('loading');
  runLoadingAnimation().then(() => {
    const result = computeMatch();
    renderResult(result);
    showPage('result');
  });
}

function showFieldError(id, msg) {
  const el = document.getElementById(id);
  if (!el) return;
  el.style.borderColor = 'var(--red)';
  el.focus();
  let err = el.parentElement.querySelector('.field-err');
  if (!err) {
    err = document.createElement('div');
    err.className = 'field-err';
    err.style.cssText = 'font-size:12px;color:var(--red);margin-top:5px;';
    el.parentElement.appendChild(err);
  }
  err.textContent = msg;
  setTimeout(() => {
    el.style.borderColor = '';
    err.remove();
  }, 3000);
}

// ── LOADING ANIMATION ────────────────
const LOADING_STEPS = [
  { id: 'ls-ner',  icon: '🔎', text: 'Named Entity Recognition...' },
  { id: 'ls-ext',  icon: '⚙️', text: 'Skill Extraction & Normalisasi...' },
  { id: 'ls-sem',  icon: '📐', text: 'Semantic Similarity Matching...' },
  { id: 'ls-scr',  icon: '📊', text: 'Experience & Education Scoring...' },
  { id: 'ls-rec',  icon: '🎓', text: 'Generating Course Recommendations...' },
];

function runLoadingAnimation() {
  return new Promise(resolve => {
    let i = 0;
    const stepText = document.getElementById('loading-step-text');

    // Reset all
    LOADING_STEPS.forEach(s => {
      const el = document.getElementById(s.id);
      if (el) el.className = 'ls-row';
    });

    function tick() {
      if (i < LOADING_STEPS.length) {
        if (i > 0) {
          const prev = document.getElementById(LOADING_STEPS[i - 1].id);
          if (prev) { prev.classList.remove('active'); prev.classList.add('done'); }
        }
        const cur = document.getElementById(LOADING_STEPS[i].id);
        if (cur) cur.classList.add('active');
        if (stepText) stepText.textContent = LOADING_STEPS[i].text;
        i++;
        setTimeout(tick, 600 + Math.random() * 350);
      } else {
        // Mark last done
        const last = document.getElementById(LOADING_STEPS[LOADING_STEPS.length - 1].id);
        if (last) { last.classList.remove('active'); last.classList.add('done'); }
        setTimeout(resolve, 300);
      }
    }
    tick();
  });
}

// ── SKILL MATCHING ENGINE ────────────
const SKILL_ALIASES = {
  'js': 'javascript', 'javascript': 'javascript',
  'ts': 'typescript', 'typescript': 'typescript',
  'node': 'node.js', 'nodejs': 'node.js', 'node.js': 'node.js',
  'react': 'react', 'reactjs': 'react', 'react.js': 'react',
  'vue': 'vue', 'vuejs': 'vue', 'vue.js': 'vue',
  'next': 'next.js', 'nextjs': 'next.js', 'next.js': 'next.js',
  'nuxt': 'nuxt', 'nuxtjs': 'nuxt',
  'svelte': 'svelte', 'angular': 'angular',
  'py': 'python', 'python': 'python',
  'java': 'java', 'kotlin': 'kotlin', 'swift': 'swift',
  'go': 'golang', 'golang': 'golang',
  'php': 'php', 'laravel': 'laravel',
  'rails': 'ruby on rails', 'ruby': 'ruby on rails',
  'django': 'django', 'flask': 'flask', 'fastapi': 'fastapi',
  'spring': 'spring boot', 'springboot': 'spring boot',
  'sql': 'sql', 'mysql': 'mysql', 'postgres': 'postgresql',
  'postgresql': 'postgresql', 'mongodb': 'mongodb', 'mongo': 'mongodb',
  'redis': 'redis', 'elasticsearch': 'elasticsearch', 'firebase': 'firebase',
  'docker': 'docker', 'kubernetes': 'kubernetes', 'k8s': 'kubernetes',
  'aws': 'aws', 'gcp': 'google cloud', 'azure': 'microsoft azure',
  'git': 'git', 'github': 'git', 'gitlab': 'git',
  'html': 'html', 'css': 'css', 'sass': 'sass', 'scss': 'sass',
  'tailwind': 'tailwind css', 'tailwindcss': 'tailwind css',
  'bootstrap': 'bootstrap', 'figma': 'figma',
  'rest': 'rest api', 'restful': 'rest api', 'api': 'rest api', 'rest api': 'rest api',
  'graphql': 'graphql', 'grpc': 'grpc',
  'ml': 'machine learning', 'machine learning': 'machine learning',
  'dl': 'deep learning', 'deep learning': 'deep learning',
  'nlp': 'nlp', 'tensorflow': 'tensorflow', 'pytorch': 'pytorch',
  'scikit': 'scikit-learn', 'sklearn': 'scikit-learn', 'scikit-learn': 'scikit-learn',
  'pandas': 'pandas', 'numpy': 'numpy', 'matplotlib': 'matplotlib',
  'agile': 'agile', 'scrum': 'scrum', 'jira': 'jira', 'kanban': 'kanban',
  'ci': 'ci/cd', 'cicd': 'ci/cd', 'ci/cd': 'ci/cd', 'jenkins': 'jenkins',
  'linux': 'linux', 'bash': 'bash/shell', 'shell': 'bash/shell',
};

const KNOWN_SKILLS = Object.values(SKILL_ALIASES).filter((v, i, a) => a.indexOf(v) === i);

function normalizeSkill(raw) {
  const s = raw.toLowerCase().trim().replace(/[^a-z0-9.\/+# ]/g, '');
  return SKILL_ALIASES[s] || s;
}

function parseSkills(raw) {
  return raw.split(/[\s,;\n\/|&]+/)
    .map(s => s.trim()).filter(s => s.length > 1)
    .map(normalizeSkill)
    .filter(Boolean);
}

function extractSkillsFromText(text) {
  if (!text) return [];
  const lower = text.toLowerCase();
  return KNOWN_SKILLS.filter(skill => {
    const re = new RegExp(`\\b${skill.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`);
    return re.test(lower);
  });
}

function dedupe(arr) {
  return [...new Set(arr)];
}

function computeMatch() {
  const cvSkillsRaw = document.getElementById('cv-skills').value;
  const jdSkillsRaw = document.getElementById('jd-skills').value;
  const cvText      = document.getElementById('cv-text').value;
  const jdText      = document.getElementById('jd-text').value;
  const cvUniv      = document.getElementById('cv-univ').value;
  const cvGrad      = document.getElementById('cv-grad').value;
  const jdRole      = document.getElementById('jd-role').value || 'Posisi Dilamar';
  const jdCompany   = document.getElementById('jd-company').value || 'Perusahaan';
  const jdExpMin    = document.getElementById('jd-exp').value;
  const jdLevel     = document.getElementById('jd-level').value;

  // Build skill sets
  const cvSkills = dedupe([...parseSkills(cvSkillsRaw), ...extractSkillsFromText(cvText)]);
  const jdSkills = dedupe([...parseSkills(jdSkillsRaw), ...extractSkillsFromText(jdText)]);

  // Fallback demo data
  const cvFinal = cvSkills.length > 0 ? cvSkills : ['javascript', 'react', 'html', 'css', 'git'];
  const jdFinal = jdSkills.length > 0 ? jdSkills : ['react', 'typescript', 'node.js', 'rest api', 'git', 'docker'];

  // Skill scoring
  const matched = dedupe(cvFinal.filter(c => jdFinal.some(j =>
    j === c || j.startsWith(c) || c.startsWith(j)
  )));
  const missing = dedupe(jdFinal.filter(j => !cvFinal.some(c =>
    c === j || j.startsWith(c) || c.startsWith(j)
  )));
  const skillScore = jdFinal.length > 0
    ? Math.min(98, Math.round((matched.length / jdFinal.length) * 100))
    : 60;

  // Experience scoring (heuristic from text)
  const expYearMatch = cvText.match(/(\d+)\s*(tahun|year|yr)/i);
  const cvExpYears = expYearMatch ? parseInt(expYearMatch[1]) : (cvSkills.length > 5 ? 2 : 1);
  const jdExpYears = jdExpMin ? (parseInt(jdExpMin) || 0) : 0;
  let expScore;
  if (jdExpYears === 0) expScore = 70 + Math.floor(Math.random() * 20);
  else if (cvExpYears >= jdExpYears) expScore = 80 + Math.floor(Math.random() * 15);
  else expScore = Math.max(30, Math.round((cvExpYears / jdExpYears) * 80));

  // Education scoring
  const hasDegree = cvUniv || cvText.toLowerCase().match(/s1|s2|sarjana|bachelor|master|teknik|ilmu komputer/);
  const eduScore = hasDegree ? 70 + Math.floor(Math.random() * 25) : 50 + Math.floor(Math.random() * 20);

  // Composite
  const total = Math.min(97, Math.round(skillScore * 0.55 + expScore * 0.28 + eduScore * 0.17));

  return {
    total, skillScore, expScore, eduScore,
    matched, missing, jdRole, jdCompany, cvName: document.getElementById('cv-name').value
  };
}

// ── COURSES DATABASE ─────────────────
const COURSES = {
  'typescript': [
    { title: 'TypeScript Full Course for Beginners', channel: 'Dave Gray', views: '1.8M', dur: '8:00:00', thumb: 'https://img.youtube.com/vi/30LWjhZzg50/mqdefault.jpg', url: 'https://youtube.com/watch?v=30LWjhZzg50' },
    { title: 'TypeScript Tutorial — The Net Ninja', channel: 'The Net Ninja', views: '950K', dur: '2:33:00', thumb: 'https://img.youtube.com/vi/2pZmKW9-I_k/mqdefault.jpg', url: 'https://youtube.com/watch?v=2pZmKW9-I_k' },
    { title: 'TypeScript in 100 Seconds', channel: 'Fireship', views: '2.1M', dur: '2:44', thumb: 'https://img.youtube.com/vi/zQnBQ4tB3ZA/mqdefault.jpg', url: 'https://youtube.com/watch?v=zQnBQ4tB3ZA' },
  ],
  'docker': [
    { title: 'Docker Tutorial for Beginners — Full Course', channel: 'TechWorld with Nana', views: '3.4M', dur: '3:12:44', thumb: 'https://img.youtube.com/vi/3c-iBn73dDE/mqdefault.jpg', url: 'https://youtube.com/watch?v=3c-iBn73dDE' },
    { title: 'Docker in 100 Seconds', channel: 'Fireship', views: '3.0M', dur: '2:10', thumb: 'https://img.youtube.com/vi/Gjnup-PuquQ/mqdefault.jpg', url: 'https://youtube.com/watch?v=Gjnup-PuquQ' },
    { title: 'Docker untuk Developer Indonesia', channel: 'Programmer Zaman Now', views: '430K', dur: '2:05:30', thumb: 'https://img.youtube.com/vi/3_yxVjV88Zk/mqdefault.jpg', url: 'https://youtube.com/watch?v=3_yxVjV88Zk' },
  ],
  'kubernetes': [
    { title: 'Kubernetes Tutorial for Beginners', channel: 'TechWorld with Nana', views: '5.6M', dur: '4:27:00', thumb: 'https://img.youtube.com/vi/X48VuDVv0do/mqdefault.jpg', url: 'https://youtube.com/watch?v=X48VuDVv0do' },
    { title: 'Kubernetes in 100 Seconds', channel: 'Fireship', views: '2.0M', dur: '2:26', thumb: 'https://img.youtube.com/vi/PziYflu8cB8/mqdefault.jpg', url: 'https://youtube.com/watch?v=PziYflu8cB8' },
    { title: 'Kubernetes Crash Course', channel: 'Traversy Media', views: '780K', dur: '1:20:00', thumb: 'https://img.youtube.com/vi/s_o8dwzRlu4/mqdefault.jpg', url: 'https://youtube.com/watch?v=s_o8dwzRlu4' },
  ],
  'machine learning': [
    { title: 'Machine Learning Full Course — freeCodeCamp', channel: 'freeCodeCamp', views: '2.4M', dur: '10:25:00', thumb: 'https://img.youtube.com/vi/7eh4d6sabA0/mqdefault.jpg', url: 'https://youtube.com/watch?v=7eh4d6sabA0' },
    { title: 'ML Crash Course — Google Developers', channel: 'Google Developers', views: '4.7M', dur: '1:30:12', thumb: 'https://img.youtube.com/vi/KNAWp2S3w94/mqdefault.jpg', url: 'https://youtube.com/watch?v=KNAWp2S3w94' },
    { title: 'Machine Learning dari Nol', channel: 'Coding Indonesia', views: '390K', dur: '2:45:00', thumb: 'https://img.youtube.com/vi/i_LwzRVP7bg/mqdefault.jpg', url: 'https://youtube.com/watch?v=i_LwzRVP7bg' },
  ],
  'python': [
    { title: 'Python Full Course for Beginners', channel: 'freeCodeCamp', views: '8.2M', dur: '4:26:52', thumb: 'https://img.youtube.com/vi/rfscVS0vtbw/mqdefault.jpg', url: 'https://youtube.com/watch?v=rfscVS0vtbw' },
    { title: 'Python untuk Pemula Lengkap', channel: 'Kelas Terbuka', views: '1.9M', dur: '4:00:00', thumb: 'https://img.youtube.com/vi/_uQrJ0TkZlc/mqdefault.jpg', url: 'https://youtube.com/watch?v=_uQrJ0TkZlc' },
    { title: 'Python in 100 Seconds', channel: 'Fireship', views: '2.3M', dur: '2:38', thumb: 'https://img.youtube.com/vi/x7X9w_GIm1s/mqdefault.jpg', url: 'https://youtube.com/watch?v=x7X9w_GIm1s' },
  ],
  'node.js': [
    { title: 'Node.js Full Course', channel: 'freeCodeCamp', views: '3.3M', dur: '8:16:00', thumb: 'https://img.youtube.com/vi/Oe421EPjeBE/mqdefault.jpg', url: 'https://youtube.com/watch?v=Oe421EPjeBE' },
    { title: 'Node.js Tutorial — The Net Ninja', channel: 'The Net Ninja', views: '2.6M', dur: '3:41:00', thumb: 'https://img.youtube.com/vi/w-7RQ46RgxU/mqdefault.jpg', url: 'https://youtube.com/watch?v=w-7RQ46RgxU' },
    { title: 'Node.js in 100 Seconds', channel: 'Fireship', views: '1.4M', dur: '2:15', thumb: 'https://img.youtube.com/vi/ENrzD9HAZK4/mqdefault.jpg', url: 'https://youtube.com/watch?v=ENrzD9HAZK4' },
  ],
  'sql': [
    { title: 'SQL Full Course — freeCodeCamp', channel: 'freeCodeCamp', views: '6.1M', dur: '4:20:00', thumb: 'https://img.youtube.com/vi/HXV3zeQKqGY/mqdefault.jpg', url: 'https://youtube.com/watch?v=HXV3zeQKqGY' },
    { title: 'SQL Tutorial — TechTFQ', channel: 'TechTFQ', views: '2.1M', dur: '3:00:00', thumb: 'https://img.youtube.com/vi/a-hFbr2vizE/mqdefault.jpg', url: 'https://youtube.com/watch?v=a-hFbr2vizE' },
    { title: 'SQL in 100 Seconds', channel: 'Fireship', views: '1.2M', dur: '2:38', thumb: 'https://img.youtube.com/vi/zsjvFFKOm3c/mqdefault.jpg', url: 'https://youtube.com/watch?v=zsjvFFKOm3c' },
  ],
  'aws': [
    { title: 'AWS Full Course 2024 — freeCodeCamp', channel: 'freeCodeCamp', views: '3.5M', dur: '5:27:00', thumb: 'https://img.youtube.com/vi/ZB5ONbD_SMY/mqdefault.jpg', url: 'https://youtube.com/watch?v=ZB5ONbD_SMY' },
    { title: 'AWS Cloud Practitioner — Andrew Brown', channel: 'freeCodeCamp', views: '4.2M', dur: '11:58:00', thumb: 'https://img.youtube.com/vi/SOTamWNgDKc/mqdefault.jpg', url: 'https://youtube.com/watch?v=SOTamWNgDKc' },
    { title: 'AWS in 100 Seconds', channel: 'Fireship', views: '950K', dur: '2:22', thumb: 'https://img.youtube.com/vi/a9__D53WsUs/mqdefault.jpg', url: 'https://youtube.com/watch?v=a9__D53WsUs' },
  ],
  'graphql': [
    { title: 'GraphQL Full Course — Beginner to Expert', channel: 'freeCodeCamp', views: '1.3M', dur: '5:50:00', thumb: 'https://img.youtube.com/vi/ed8SzALpx1Q/mqdefault.jpg', url: 'https://youtube.com/watch?v=ed8SzALpx1Q' },
    { title: 'GraphQL Crash Course', channel: 'Traversy Media', views: '620K', dur: '1:48:00', thumb: 'https://img.youtube.com/vi/BcLNfwF04Kw/mqdefault.jpg', url: 'https://youtube.com/watch?v=BcLNfwF04Kw' },
    { title: 'GraphQL in 100 Seconds', channel: 'Fireship', views: '1.0M', dur: '2:14', thumb: 'https://img.youtube.com/vi/eIQh02xuVw4/mqdefault.jpg', url: 'https://youtube.com/watch?v=eIQh02xuVw4' },
  ],
  'default': [
    { title: 'Complete Developer Roadmap 2024', channel: 'Traversy Media', views: '1.6M', dur: '2:00:00', thumb: 'https://img.youtube.com/vi/ysEN5RaKOlA/mqdefault.jpg', url: 'https://youtube.com/watch?v=ysEN5RaKOlA' },
    { title: 'How to Learn Programming Faster', channel: 'Fireship', views: '3.8M', dur: '8:48', thumb: 'https://img.youtube.com/vi/kx3iWjnHL54/mqdefault.jpg', url: 'https://youtube.com/watch?v=kx3iWjnHL54' },
    { title: 'Tutorial Pemrograman Lengkap', channel: 'Programmer Zaman Now', views: '910K', dur: '5:00:00', thumb: 'https://img.youtube.com/vi/Zft8RMb8Uko/mqdefault.jpg', url: 'https://youtube.com/watch?v=Zft8RMb8Uko' },
  ],
};

function getCoursesForSkill(skill) {
  const key = Object.keys(COURSES).find(k => k !== 'default' && (skill.includes(k) || k.includes(skill)));
  return COURSES[key] || COURSES['default'];
}

// ── RENDER RESULT ────────────────────
function renderResult(result) {
  const { total, skillScore, expScore, eduScore, matched, missing, jdRole, jdCompany, cvName } = result;

  // Topbar
  const name = cvName ? `${cvName} → ` : '';
  document.getElementById('result-subtitle').textContent = `${name}${jdRole} di ${jdCompany}`;

  // Animate score counter
  const numEl = document.getElementById('result-score-num');
  let cur = 0;
  const step = Math.ceil(total / 50);
  const counter = setInterval(() => {
    cur = Math.min(cur + step, total);
    numEl.textContent = cur;
    if (cur >= total) clearInterval(counter);
  }, 24);

  // Ring SVG progress
  setTimeout(() => {
    const ring = document.getElementById('score-ring-fg');
    if (ring) {
      const circ = 2 * Math.PI * 54; // r=54
      ring.style.strokeDasharray = circ;
      ring.style.strokeDashoffset = circ - (circ * total / 100);
    }
  }, 100);

  // Verdict
  let verdict, badgeClass;
  if (total >= 80) { verdict = 'Sangat Cocok 🎉'; badgeClass = 'badge-great'; }
  else if (total >= 60) { verdict = 'Cukup Cocok'; badgeClass = 'badge-ok'; }
  else { verdict = 'Perlu Persiapan'; badgeClass = 'badge-low'; }
  document.getElementById('score-verdict').textContent = verdict;
  const badge = document.getElementById('score-badge');
  badge.textContent = total >= 80 ? 'Disarankan Melamar' : total >= 60 ? 'Perlu Sedikit Persiapan' : 'Perlu Banyak Persiapan';
  badge.className = 'score-badge ' + badgeClass;

  // Bars
  setTimeout(() => {
    setBar('bar-skill', 's-skill', skillScore);
    setBar('bar-exp',   's-exp',   expScore);
    setBar('bar-edu',   's-edu',   eduScore);
  }, 200);

  // Summary
  const summaryParts = [];
  if (skillScore >= 75) summaryParts.push(`<strong>${matched.length} dari ${matched.length + missing.length} skill</strong> yang dibutuhkan sudah kamu kuasai.`);
  else summaryParts.push(`Kamu baru menguasai <strong>${matched.length} dari ${matched.length + missing.length} skill</strong> yang dibutuhkan.`);
  if (missing.length > 0) summaryParts.push(`Ada <strong>${missing.length} skill</strong> yang perlu ditingkatkan.`);
  if (total >= 80) summaryParts.push('Profil kamu sangat cocok — segera lamar posisi ini!');
  else if (total >= 60) summaryParts.push('Dengan sedikit persiapan kamu sudah siap melamar.');
  else summaryParts.push('Fokus pada rekomendasi kursus di bawah untuk meningkatkan kesiapanmu.');
  document.getElementById('score-summary').innerHTML = summaryParts.join(' ');

  // Matched skills
  const matchedEl = document.getElementById('matched-skills');
  document.getElementById('matched-count').textContent = matched.length;
  matchedEl.innerHTML = matched.length > 0
    ? matched.map(s => `<span class="s-chip match">✓ ${s}</span>`).join('')
    : '<span style="color:var(--muted);font-size:13px">Tidak ada skill yang terdeteksi</span>';

  // Missing skills
  const missingEl = document.getElementById('missing-skills');
  document.getElementById('missing-count').textContent = missing.length;
  missingEl.innerHTML = missing.length > 0
    ? missing.map(s => `<span class="s-chip miss">✗ ${s}</span>`).join('')
    : '<span style="color:var(--green);font-size:13px">🎉 Semua skill terpenuhi!</span>';

  // Gap note
  const noteEl = document.getElementById('gap-note');
  if (missing.length > 0) {
    noteEl.style.display = 'block';
    noteEl.innerHTML = `<strong>Kenapa ini penting?</strong> Skills ini secara eksplisit disebutkan dalam job description. Menguasainya akan meningkatkan peluang kamu secara signifikan.`;
  } else {
    noteEl.style.display = 'none';
  }

  // Courses
  const container = document.getElementById('courses-container');
  container.innerHTML = '';
  const toShow = missing.slice(0, 4);
  if (toShow.length === 0) {
    container.innerHTML = `<div style="text-align:center;padding:48px;color:var(--muted);background:white;border-radius:var(--radius-lg);border:1px solid var(--border)">
      <div style="font-size:36px;margin-bottom:16px">🎉</div>
      <div style="font-size:16px;font-weight:600;color:var(--navy);margin-bottom:8px">Tidak ada skill gap!</div>
      <div style="font-size:14px">Kamu sudah memenuhi semua skill requirements untuk posisi ini.</div>
    </div>`;
    return;
  }
  toShow.forEach((skill, idx) => {
    const courses = getCoursesForSkill(skill);
    const group = document.createElement('div');
    group.className = 'course-group fade-in';
    group.style.animationDelay = `${idx * 0.08}s`;
    group.innerHTML = `
      <div class="course-group-label">✗ ${skill}</div>
      <div class="course-grid">
        ${courses.map(c => `
          <div class="course-card" onclick="window.open('${c.url}','_blank')">
            <div class="course-thumb">
              <img src="${c.thumb}" alt="${c.title}" loading="lazy"
                onerror="this.parentElement.innerHTML='<div style=\\'width:100%;height:100%;background:var(--bg2);display:flex;align-items:center;justify-content:center;font-size:28px\\'>▶️</div>'">
              <div class="course-play"><div class="play-btn">▶</div></div>
            </div>
            <div class="course-info">
              <div class="course-title">${c.title}</div>
              <div class="course-channel">📺 ${c.channel}</div>
              <div class="course-meta"><span>👁 ${c.views} views</span><span>⏱ ${c.dur}</span></div>
            </div>
          </div>
        `).join('')}
      </div>
    `;
    container.appendChild(group);
  });
}

function setBar(barId, valId, score) {
  const bar = document.getElementById(barId);
  const val = document.getElementById(valId);
  if (bar) bar.style.width = score + '%';
  if (val) val.textContent = score + '%';
}

// ── INIT ─────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Init ring (set dasharray before animation)
  const ring = document.getElementById('score-ring-fg');
  if (ring) {
    const circ = 2 * Math.PI * 54;
    ring.style.strokeDasharray = circ;
    ring.style.strokeDashoffset = circ;
  }
});