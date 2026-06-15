import sys

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Instead of relying on emojis, just split by <script> for the JS part
script_split = content.split('<script>')
if len(script_split) < 2:
    print("Could not find <script>")
    sys.exit(1)
    
html_part = script_split[0]
script_part = '<script>' + script_split[1]

# Now split html_part by the major pages
# We know the pages use id="page-xxx"
# Let's just regex extract them by id!

import re

# Find head and nav of landing
head_match = re.search(r'(<!DOCTYPE html>.*?)<div id="page-landing"', html_part, re.DOTALL)
head = head_match.group(1)

# Extract sections
landing = re.search(r'(<div id="page-landing".*?)<div id="page-login"', html_part, re.DOTALL).group(1)
login = re.search(r'(<div id="page-login".*?)<div id="page-register"', html_part, re.DOTALL).group(1)
register = re.search(r'(<div id="page-register".*?)<div id="page-profile"', html_part, re.DOTALL).group(1)

profile = re.search(r'(<div id="page-profile".*?)<div id="page-dashboard"', html_part, re.DOTALL).group(1)
dashboard = re.search(r'(<div id="page-dashboard".*?)<div id="page-analysis"', html_part, re.DOTALL).group(1)
analysis = re.search(r'(<div id="page-analysis".*?)<div id="page-upgrade"', html_part, re.DOTALL).group(1)
upgrade = re.search(r'(<div id="page-upgrade".*?)<div id="page-rec-app"', html_part, re.DOTALL).group(1)

# Rec-app goes until the end of the pages. The pages are closed before overlays.
# Look for the last closing div before the overlays. Let's just match until '<div class="loading-overlay"'
rec_app_match = re.search(r'(<div id="page-rec-app".*?)<div class="loading-overlay"', html_part, re.DOTALL)
rec_app = rec_app_match.group(1)

# The rest of html_part is the modals
modals = '<div class="loading-overlay"' + html_part.split('<div class="loading-overlay"')[1]

# BUILD INDEX.HTML (Landing + Login + Register)
landing_html = head + landing + login + register + modals
landing_script = script_part.replace("goTo('rec-app');", "window.location.href = 'recruiter.html';")
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
js_script = script_part.replace("function goTo(page, skipHistory = false) {", """function goTo(page, skipHistory = false) {
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
rec_html = head + rec_app + modals
rec_script = script_part.replace("function goTo(page, skipHistory = false) {", """function goTo(page, skipHistory = false) {
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

print("Split using Div IDs completed successfully!")
