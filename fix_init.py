import os

def append_init(filename, init_script):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We remove the old INIT block if we added it, but just safely replace it.
    if "// ── INIT ──" in content:
        parts = content.split("// ── INIT ──")
        new_content = parts[0] + "// ── INIT ──\n" + init_script + "\n</script>\n</body>\n</html>"
    else:
        # Just append before </script>
        new_content = content.replace("</script>", "\n// ── INIT ──\n" + init_script + "\n</script>")

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)

mainfinal_init = """
  if (!currentUser || currentRole !== 'jobseeker') {
    window.location.href = 'index.html';
  } else {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById('page-dashboard').classList.add('active');
    updateJSDashboard();
    if (!profileData.done) {
        document.getElementById('p-name').value = currentUser.name;
        if (currentUser.field) document.getElementById('p-field').value = currentUser.field;
        goTo('profile', true);
    }
  }
"""

recruiter_init = """
  if (!currentUser || currentRole !== 'recruiter') {
    window.location.href = 'index.html';
  } else {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById('page-rec-app').classList.add('active');
    initRecruiterApp();
  }
"""

index_init = """
  if (currentUser) {
    if (currentRole === 'recruiter') window.location.href = 'recruiter.html';
    else window.location.href = 'mainfinal.html';
  }
"""

append_init('mainfinal.html', mainfinal_init)
append_init('recruiter.html', recruiter_init)
append_init('index.html', index_init)

print("Init logic updated for all 3 files!")
