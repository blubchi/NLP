import os
import sys

try:
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
except FileNotFoundError:
    print("index.html not found!")
    sys.exit(1)

# Split by the comment header lines
parts = content.split("<!-- ══════════════════════════════════════════")

head = parts[0]
landing = "<!-- ══════════════════════════════════════════" + parts[1]
login = "<!-- ══════════════════════════════════════════" + parts[2]
register = "<!-- ══════════════════════════════════════════" + parts[3]
profile = "<!-- ══════════════════════════════════════════" + parts[4]
dashboard = "<!-- ══════════════════════════════════════════" + parts[5]
analysis = "<!-- ══════════════════════════════════════════" + parts[6]
upgrade = "<!-- ══════════════════════════════════════════" + parts[7]

# The recruiter part has the SHARED OVERLAYS comment inside its chunk
recruiter_and_rest = "<!-- ══════════════════════════════════════════" + parts[8]

recruiter_split = recruiter_and_rest.split("<!-- 🔮 SHARED OVERLAYS 🔮 -->")
recruiter_page = recruiter_split[0]
rest = "<!-- 🔮 SHARED OVERLAYS 🔮 -->" + recruiter_split[1]

modals_split = rest.split("<script>")
modals = modals_split[0]
script = "<script>" + modals_split[1]

# BUILD INDEX.HTML (Landing + Login + Register)
landing_html = head + landing + login + register + modals
landing_script = script.replace("goTo('rec-app');", "window.location.href = 'recruiter.html';")
landing_script = landing_script.replace("goTo('dashboard');", "window.location.href = 'mainfinal.html';")
landing_script = landing_script.replace("goTo('profile');", "window.location.href = 'mainfinal.html';")
landing_script = landing_script.replace("// Inisialisasi awal", """// Inisialisasi awal
  if (currentUser) {
    if (currentRole === 'recruiter') window.location.href = 'recruiter.html';
    else window.location.href = 'mainfinal.html';
  }
""")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(landing_html + landing_script)


# BUILD MAINFINAL.HTML (Job Seeker)
js_html = head + profile + dashboard + analysis + upgrade + modals
js_script = script.replace("function goTo(page, skipHistory = false) {", """function goTo(page, skipHistory = false) {
    if (page === 'landing' || page === 'login' || page === 'register') {
      window.location.href = 'index.html';
      return;
    }
""")
js_script = js_script.replace("// Inisialisasi awal", """// Inisialisasi awal
  if (!currentUser || currentRole !== 'jobseeker') {
    window.location.href = 'index.html';
  }
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-dashboard').classList.add('active');
""")
with open('mainfinal.html', 'w', encoding='utf-8') as f:
    f.write(js_html + js_script)


# BUILD RECRUITER.HTML (Recruiter)
rec_html = head + recruiter_page + modals
rec_script = script.replace("function goTo(page, skipHistory = false) {", """function goTo(page, skipHistory = false) {
    if (page === 'landing' || page === 'login' || page === 'register') {
      window.location.href = 'index.html';
      return;
    }
""")
rec_script = rec_script.replace("// Inisialisasi awal", """// Inisialisasi awal
  if (!currentUser || currentRole !== 'recruiter') {
    window.location.href = 'index.html';
  }
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-rec-app').classList.add('active');
""")
with open('recruiter.html', 'w', encoding='utf-8') as f:
    f.write(rec_html + rec_script)

print("Split completed successfully!")
