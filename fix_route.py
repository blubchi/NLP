def fix_route(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old_func = """  function routeAfterLogin() {
    if (!currentRole) return;
    if (currentRole === 'recruiter') {
      initRecruiterApp();
      window.location.href = 'recruiter.html';
    } else {
      document.getElementById('nav-user').textContent = currentUser.name;
      if (profileData.done) {
        window.location.href = 'mainfinal.html';
      } else {
        document.getElementById('p-name').value = currentUser.name;
        if (currentUser.field) document.getElementById('p-field').value = currentUser.field;
        window.location.href = 'mainfinal.html';
      }
    }
  }"""
    
    new_func = """  function routeAfterLogin() {
    if (!currentRole) return;
    if (currentRole === 'recruiter') {
      window.location.href = 'recruiter.html';
    } else {
      window.location.href = 'mainfinal.html';
    }
  }"""

    content = content.replace(old_func, new_func)

    # Let's also fix the Inisialisasi awal check to properly load UI data if needed.
    # In recruiter.html, it should call initRecruiterApp() on load if logged in.
    # In mainfinal.html, it should call updateJSDashboard() or prefillProfile() if needed.
    # Actually, in recruiter.html, initRecruiterApp() is probably already called?
    # Let's check how initialization is handled.

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

fix_route('index.html')
fix_route('mainfinal.html')
fix_route('recruiter.html')

print("Fixed routeAfterLogin in all files")
