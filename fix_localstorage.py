import re

def fix_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Replace state initialization
    state_init = """  // ── GLOBAL STATE ──
  let currentUser = null;
  let currentRole = null; // 'jobseeker' | 'recruiter'
  let selectedRegRole = null;

  // Job Seeker state
  let profileData = {};
  let analysisHistory = [];
  let techTagsData = [], softTagsData = [], toolsTagsData = [];
  let expCount = 0;
  let currentStep = 1;

  // Ad state
  let adInterval, adTimeoutSkip, adTimeoutClose;

  // Recruiter state
  let recUser = null;
  let vacancies = [];
  let currentCV = null;
  let recAnalysisHistory = [];
  let recruiterProfile = {
    name: "", pt: "Tech Solutions Inc.", department: "Human Resources",
    bio: "Recruiter IT berpengalaman.", companyProfile: "Perusahaan IT terkemuka."
  };
  let profileUpdateLog = [];

  const FREE_DAILY_LIMIT = 3;
  const PRO_DAILY_LIMIT = 30;

  // ── DEMO CV DATA ──"""

    new_state_init = """  // ── GLOBAL STATE ──
  let selectedRegRole = null;
  let expCount = 0;
  let currentStep = 1;
  let adInterval, adTimeoutSkip, adTimeoutClose;
  let currentCV = null;

  const FREE_DAILY_LIMIT = 3;
  const PRO_DAILY_LIMIT = 30;

  // Default states
  let currentUser = null;
  let currentRole = null;
  let profileData = {};
  let analysisHistory = [];
  let techTagsData = [], softTagsData = [], toolsTagsData = [];
  let vacancies = [];
  let recAnalysisHistory = [];
  let recruiterProfile = { name: "", pt: "Tech Solutions Inc.", department: "Human Resources", bio: "Recruiter IT berpengalaman.", companyProfile: "Perusahaan IT terkemuka." };
  let profileUpdateLog = [];
  let accounts = {};

  function loadData() {
    try {
      const cu = localStorage.getItem('fs_currentUser'); if(cu) currentUser = JSON.parse(cu);
      const cr = localStorage.getItem('fs_currentRole'); if(cr) currentRole = cr;
      const pd = localStorage.getItem('fs_profileData'); if(pd) profileData = JSON.parse(pd);
      const ah = localStorage.getItem('fs_analysisHistory'); if(ah) analysisHistory = JSON.parse(ah);
      const tt = localStorage.getItem('fs_techTagsData'); if(tt) techTagsData = JSON.parse(tt);
      const st = localStorage.getItem('fs_softTagsData'); if(st) softTagsData = JSON.parse(st);
      const to = localStorage.getItem('fs_toolsTagsData'); if(to) toolsTagsData = JSON.parse(to);
      const vc = localStorage.getItem('fs_vacancies'); if(vc) vacancies = JSON.parse(vc);
      const rh = localStorage.getItem('fs_recAnalysisHistory'); if(rh) recAnalysisHistory = JSON.parse(rh);
      const rp = localStorage.getItem('fs_recruiterProfile'); if(rp) recruiterProfile = JSON.parse(rp);
      const pl = localStorage.getItem('fs_profileUpdateLog'); if(pl) profileUpdateLog = JSON.parse(pl);
      const ac = localStorage.getItem('fs_accounts'); if(ac) accounts = JSON.parse(ac);
    } catch(e) { console.error("Error loading localStorage", e); }
  }

  function saveData() {
    try {
      localStorage.setItem('fs_currentUser', JSON.stringify(currentUser));
      localStorage.setItem('fs_currentRole', currentRole || '');
      localStorage.setItem('fs_profileData', JSON.stringify(profileData));
      localStorage.setItem('fs_analysisHistory', JSON.stringify(analysisHistory));
      localStorage.setItem('fs_techTagsData', JSON.stringify(techTagsData));
      localStorage.setItem('fs_softTagsData', JSON.stringify(softTagsData));
      localStorage.setItem('fs_toolsTagsData', JSON.stringify(toolsTagsData));
      localStorage.setItem('fs_vacancies', JSON.stringify(vacancies));
      localStorage.setItem('fs_recAnalysisHistory', JSON.stringify(recAnalysisHistory));
      localStorage.setItem('fs_recruiterProfile', JSON.stringify(recruiterProfile));
      localStorage.setItem('fs_profileUpdateLog', JSON.stringify(profileUpdateLog));
      localStorage.setItem('fs_accounts', JSON.stringify(accounts));
    } catch(e) { console.error("Error saving localStorage", e); }
  }

  loadData();

  // ── DEMO CV DATA ──"""

    content = content.replace(state_init, new_state_init)

    # Remove the old accounts array declaration
    content = content.replace("// ── ACCOUNTS STORAGE (in-memory, survives page navigation) ──\n  const accounts = {}; // keyed by email\n", "")
    content = content.replace("// ── ACCOUNTS STORAGE (in-memory, survives page navigation) ──\r\n  const accounts = {}; // keyed by email\r\n", "")

    # Inject saveData() into key functions
    # 1. doLogin
    content = content.replace("showToast('Login berhasil!');\n    routeAfterLogin();", "saveData();\n    showToast('Login berhasil!');\n    setTimeout(routeAfterLogin, 500);")
    content = content.replace("showToast('Login berhasil! Selamat datang, ' + acc.name + ' 👋');\n      routeAfterLogin();", "saveData();\n      showToast('Login berhasil! Selamat datang, ' + acc.name + ' 👋');\n      setTimeout(routeAfterLogin, 500);")
    
    # 2. doRegister
    content = content.replace("showToast('Akun berhasil dibuat! 🎉');\n    routeAfterLogin();", "saveData();\n    showToast('Akun berhasil dibuat! 🎉');\n    setTimeout(routeAfterLogin, 500);")

    # 3. doLogout
    content = content.replace("showToast('Berhasil keluar.');", "saveData();\n    showToast('Berhasil keluar.');")

    # 4. finishProfile
    content = content.replace("showToast('Profil berhasil disimpan! 🎉');\n    window.location.href = 'mainfinal.html';", "saveData();\n    showToast('Profil berhasil disimpan! 🎉');\n    setTimeout(() => { window.location.href = 'mainfinal.html'; }, 500);")

    # 5. executeAnalysis
    content = content.replace("jd, req\n      });", "jd, req\n      });\n      saveData();")

    # 6. runRecruiterAnalysis
    content = content.replace("recAnalysisHistory.push({", "saveData();\n      recAnalysisHistory.push({")
    
    # 7. saveVacancy
    content = content.replace("document.getElementById('req-list').innerHTML='<div class=\"req-row\"><input type=\"text\" placeholder=\"Requirement...\"><button class=\"req-del\" onclick=\"delReq(this)\">×</button></div>';", "document.getElementById('req-list').innerHTML='<div class=\"req-row\"><input type=\"text\" placeholder=\"Requirement...\"><button class=\"req-del\" onclick=\"delReq(this)\">×</button></div>';\n    saveData();")

    # 8. deleteVacancy
    content = content.replace("function deleteVacancy(i){vacancies.splice(i,1);document.getElementById('stat-vac').textContent=vacancies.length;renderVacancyGrid();}", "function deleteVacancy(i){vacancies.splice(i,1);saveData();document.getElementById('stat-vac').textContent=vacancies.length;renderVacancyGrid();}")

    # 9. saveRecruiterProfile
    content = content.replace("renderProfileLog();\n    showToast('Profil berhasil disimpan!');", "saveData();\n    renderProfileLog();\n    showToast('Profil berhasil disimpan!');")

    # Fix routeAfterLogin so it doesn't crash if currentRole is null
    content = content.replace("if (currentRole === 'recruiter') {", "if (!currentRole) return;\n    if (currentRole === 'recruiter') {")

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

fix_file('index.html')
fix_file('mainfinal.html')
fix_file('recruiter.html')

print("localStorage fix applied to all 3 files!")
