import re
import os
import sys

try:
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
except FileNotFoundError:
    print("index.html not found!")
    sys.exit(1)

head_match = re.search(r'(<!DOCTYPE html>.*?</head>\s*<body>)', content, re.DOTALL)
head = head_match.group(1)

landing_match = re.search(r'(<!-- ══════════════════════════════════════════\s*PAGE: LANDING\s*══════════════════════════════════════════ -->(?:.+?))<!-- ══════════════════════════════════════════\s*PAGE: JOB SEEKER - PROFILE SETUP', content, re.DOTALL)
landing_auth = landing_match.group(1)

jobseeker_match = re.search(r'(<!-- ══════════════════════════════════════════\s*PAGE: JOB SEEKER - PROFILE SETUP(?:.+?))<!-- ══════════════════════════════════════════\s*PAGE: RECRUITER APP', content, re.DOTALL)
jobseeker_pages = jobseeker_match.group(1)

recruiter_match = re.search(r'(<!-- ══════════════════════════════════════════\s*PAGE: RECRUITER APP(?:.+?))<!-- 🔮 SHARED OVERLAYS 🔮 -->', content, re.DOTALL)
recruiter_page = recruiter_match.group(1)

modals_match = re.search(r'(<!-- 🔮 SHARED OVERLAYS 🔮 -->(?:.+?))<script>', content, re.DOTALL)
modals = modals_match.group(1)

script_match = re.search(r'(<script>.*?</script>\s*</body>\s*</html>)', content, re.DOTALL)
script = script_match.group(1)


# ==========================================
# 1. CREATE INDEX.HTML (LANDING/LOGIN/REGISTER ONLY)
# ==========================================
landing_html = head + '\n' + landing_auth + '\n' + modals + '\n'
landing_script = script.replace("goTo('rec-app');", "window.location.href = 'recruiter.html';")
landing_script = landing_script.replace("goTo('dashboard');", "window.location.href = 'mainfinal.html';")
landing_script = landing_script.replace("goTo('profile');", "window.location.href = 'mainfinal.html';")

# Redirect if already logged in
landing_script = landing_script.replace("// Inisialisasi awal", """// Inisialisasi awal
  if (currentUser) {
    if (currentRole === 'recruiter') window.location.href = 'recruiter.html';
    else window.location.href = 'mainfinal.html';
  }
""")

landing_html += landing_script
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(landing_html)


# ==========================================
# 2. CREATE MAINFINAL.HTML (JOB SEEKER ONLY)
# ==========================================
js_html = head + '\n' + jobseeker_pages + '\n' + modals + '\n'

# Modify script for JS
js_script = script.replace("function goTo(page, skipHistory = false) {", """function goTo(page, skipHistory = false) {
    if (page === 'landing' || page === 'login' || page === 'register') {
      window.location.href = 'index.html';
      return;
    }
""")
# JS on load check
js_script = js_script.replace("// Inisialisasi awal", """// Inisialisasi awal
  if (!currentUser || currentRole !== 'jobseeker') {
    window.location.href = 'index.html';
  }
  
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-dashboard').classList.add('active');
""")

js_html += js_script
with open('mainfinal.html', 'w', encoding='utf-8') as f:
    f.write(js_html)


# ==========================================
# 3. CREATE RECRUITER.HTML (RECRUITER ONLY)
# ==========================================
rec_html = head + '\n' + recruiter_page + '\n' + modals + '\n'

rec_script = script.replace("function goTo(page, skipHistory = false) {", """function goTo(page, skipHistory = false) {
    if (page === 'landing' || page === 'login' || page === 'register') {
      window.location.href = 'index.html';
      return;
    }
""")
# Recruiter on load check
rec_script = rec_script.replace("// Inisialisasi awal", """// Inisialisasi awal
  if (!currentUser || currentRole !== 'recruiter') {
    window.location.href = 'index.html';
  }
  
  // paksa active ke rec-app
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-rec-app').classList.add('active');
""")

rec_html += rec_script
with open('recruiter.html', 'w', encoding='utf-8') as f:
    f.write(rec_html)

print("Split into index.html, mainfinal.html, and recruiter.html completed successfully!")
