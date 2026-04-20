from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

tokenizer = AutoTokenizer.from_pretrained(".")
model = AutoModelForTokenClassification.from_pretrained(".")


def extract_entities(text):
    """Ekstrak token skill/entitas dari teks menggunakan model NER."""
    if not text or not text.strip():
        return []

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model(**inputs)

    logits = outputs.logits
    predictions = torch.argmax(logits, dim=2)

    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])

    entities = []
    for token, pred in zip(tokens, predictions[0]):
        label = model.config.id2label[pred.item()]
        # Ambil semua token yang bukan "O" dan bukan token spesial BERT
        if label != "O" and not token.startswith("[") and token != "##":
            # Bersihkan subword prefix "##"
            clean = token.replace("##", "").strip()
            if clean:
                entities.append(clean.lower())

    return list(set(entities))


def build_profile_text_from_structured(profile: dict) -> str:
    """
    Konversi data profil terstruktur dari frontend menjadi teks naratif
    untuk diproses oleh model NER.
    """
    parts = []

    if profile.get("name"):
        parts.append(f"Name: {profile['name']}")
    if profile.get("field"):
        parts.append(f"Field: {profile['field']}")
    if profile.get("years_exp"):
        parts.append(f"Experience: {profile['years_exp']}")
    if profile.get("summary"):
        parts.append(profile["summary"])

    # Gabungkan pengalaman kerja
    for exp in profile.get("experiences", []):
        desc = exp.get("description", "")
        position = exp.get("position", "")
        company = exp.get("company", "")
        if position or company or desc:
            parts.append(f"{position} at {company}. {desc}")

    # Gabungkan skill
    tech = profile.get("tech_skills", [])
    tools = profile.get("tools", [])
    soft = profile.get("soft_skills", [])
    all_skills = tech + tools + soft
    if all_skills:
        parts.append("Skills: " + ", ".join(all_skills))

    # Pendidikan
    edu = profile.get("education", {})
    if edu.get("school"):
        parts.append(
            f"Education: {edu.get('degree','')} {edu.get('major','')}, {edu['school']}"
        )

    return ". ".join(filter(None, parts))


def compute_scores(profile: dict, jd_skills: list, profile_skills: list):
    """
    Hitung skor breakdown berdasarkan data profil terstruktur
    dan skill yang diekstrak dari JD vs profil.
    """
    match_skills = set(jd_skills) & set(profile_skills)
    skill_score = int((len(match_skills) / len(jd_skills)) * 100) if jd_skills else 0

    # ── Skor Pengalaman ──
    years_raw = profile.get("years_exp", "") or ""
    if "5+" in years_raw or "lebih" in years_raw.lower():
        exp_score = 90
    elif "3" in years_raw or "4" in years_raw or "5" in years_raw:
        exp_score = 75
    elif "1" in years_raw or "2" in years_raw:
        exp_score = 55
    else:
        exp_score = 35

    # Bonus jika ada pengalaman kerja yang diisi
    experiences = profile.get("experiences", [])
    filled_exp = [e for e in experiences if e.get("position") or e.get("description")]
    if filled_exp:
        exp_score = min(100, exp_score + 10)

    # ── Skor Pendidikan ──
    edu = profile.get("education", {})
    degree = (edu.get("degree") or "").lower()
    if any(d in degree for d in ["s2", "master", "magister", "s3", "doktor", "phd"]):
        edu_score = 90
    elif any(d in degree for d in ["s1", "sarjana", "bachelor", "d4"]):
        edu_score = 75
    elif any(d in degree for d in ["d3", "diploma"]):
        edu_score = 60
    elif edu.get("school"):
        edu_score = 50
    else:
        edu_score = 40

    # ── Skor Soft Skill ──
    soft_skills = profile.get("soft_skills", [])
    soft_score = min(100, 40 + len(soft_skills) * 10)

    return skill_score, exp_score, edu_score, soft_score


def predict(inputs):
    """
    Entry point handler yang dipanggil oleh Hugging Face Inference API.

    Input dari mainfinal.html (buildPayload):
    {
        "jd":           string  — job description
        "req":          string  — requirements
        "profile_text": string  — teks naratif profil (fallback)
        "profile":      object  — data profil terstruktur (diutamakan)
    }

    Output yang diharapkan mapModelToUI di mainfinal.html:
    {
        "overall_score":    int 0–100
        "skill_score":      int 0–100
        "experience_score": int 0–100
        "education_score":  int 0–100
        "soft_score":       int 0–100
        "job_title":        string
        "summary":          string
        "skill_gap":        [{"name": string, "status": "match"|"miss"}]
        "recommendations":  [{"skill": string, "desc": string}]
    }
    """
    jd           = inputs.get("jd", "")
    req          = inputs.get("req", "")
    profile_obj  = inputs.get("profile", {})
    profile_text = inputs.get("profile_text", "")

    # ── Bangun teks profil dari data terstruktur jika ada, fallback ke profile_text ──
    if profile_obj:
        full_profile_text = build_profile_text_from_structured(profile_obj)
        if not full_profile_text.strip():
            full_profile_text = profile_text
    else:
        full_profile_text = profile_text

    # ── Ekstrak skill dengan model NER ──
    jd_skills      = extract_entities(jd + " " + req)
    profile_skills = extract_entities(full_profile_text)

    # Tambahkan skill eksplisit dari profil terstruktur ke profile_skills
    if profile_obj:
        explicit_skills = (
            [s.lower() for s in profile_obj.get("tech_skills", [])]
            + [s.lower() for s in profile_obj.get("tools", [])]
            + [s.lower() for s in profile_obj.get("soft_skills", [])]
        )
        profile_skills = list(set(profile_skills + explicit_skills))

    # ── Hitung kecocokan ──
    match_skills   = set(jd_skills) & set(profile_skills)
    missing_skills = set(jd_skills) - set(profile_skills)

    # ── Hitung semua skor ──
    skill_score, exp_score, edu_score, soft_score = compute_scores(
        profile_obj, jd_skills, profile_skills
    )

    # ── Overall score: rata-rata tertimbang ──
    overall_score = int(
        skill_score * 0.50
        + exp_score  * 0.25
        + edu_score  * 0.15
        + soft_score * 0.10
    )

    # ── Job title dari profil atau fallback ──
    job_title = profile_obj.get("field") or "Posisi yang Dilamar"

    # ── Summary ──
    n_match   = len(match_skills)
    n_jd      = len(jd_skills)
    n_missing = len(missing_skills)

    if overall_score >= 75:
        summary = (
            f"Profilmu sangat cocok untuk posisi ini! "
            f"Kamu memiliki {n_match} dari {n_jd} skill yang dibutuhkan. "
            f"{'Masih ada ' + str(n_missing) + ' skill yang bisa ditingkatkan.' if n_missing else 'Semua skill utama sudah kamu kuasai.'}"
        )
    elif overall_score >= 55:
        summary = (
            f"Profilmu cukup cocok. "
            f"Kamu memiliki {n_match} dari {n_jd} skill JD. "
            f"Ada {n_missing} skill teknis yang perlu dipelajari untuk memperkuat lamaranmu."
        )
    else:
        summary = (
            f"Ada beberapa gap yang perlu ditutup. "
            f"Kamu memiliki {n_match} dari {n_jd} skill yang dibutuhkan. "
            f"Fokus dulu pada {min(n_missing, 3)} skill utama yang paling sering muncul di JD ini."
        )

    # ── Skill gap — format {name, status} sesuai mapModelToUI ──
    skill_gap = (
        [{"name": s, "status": "match"} for s in sorted(match_skills)]
        + [{"name": s, "status": "miss"}  for s in sorted(missing_skills)]
    )

    # Fallback jika tidak ada skill terdeteksi
    if not skill_gap:
        skill_gap = [{"name": "Skill tidak terdeteksi dari teks JD", "status": "miss"}]

    # ── Rekomendasi — format {skill, desc} sesuai mapModelToUI ──
    rec_templates = {
        "python":      "Pelajari Python di Dicoding atau Coursera — sangat relevan untuk posisi ini.",
        "sql":         "Kuasai SQL dasar hingga intermediate di SQLZoo atau Mode Analytics.",
        "javascript":  "Pelajari JavaScript modern (ES6+) di freeCodeCamp atau The Odin Project.",
        "react":       "Ikuti kursus React di Udemy atau dokumentasi resmi react.dev.",
        "java":        "Perdalam Java OOP di Codecademy atau buku Effective Java.",
        "docker":      "Pelajari containerisasi Docker di Docker's official docs atau Play with Docker.",
        "git":         "Kuasai Git workflow di learngitbranching.js.org.",
        "machine learning": "Mulai dengan kursus ML Andrew Ng di Coursera.",
        "komunikasi":  "Tingkatkan kemampuan komunikasi dengan bergabung Toastmasters atau public speaking online.",
        "teamwork":    "Ikuti proyek open-source atau hackathon untuk melatih kolaborasi tim.",
    }

    recommendations = []
    for skill in list(missing_skills)[:5]:
        desc = rec_templates.get(
            skill.lower(),
            f"Pelajari {skill} melalui kursus online atau dokumentasi resmi untuk meningkatkan peluangmu."
        )
        recommendations.append({"skill": skill, "desc": desc})

    if not recommendations:
        recommendations = [{
            "skill": "Kembangkan Portofolio",
            "desc":  "Buat proyek nyata dan upload ke GitHub untuk memperkuat profilmu."
        }]

    return {
        "overall_score":    overall_score,
        "skill_score":      skill_score,
        "experience_score": exp_score,
        "education_score":  edu_score,
        "soft_score":       soft_score,
        "job_title":        job_title,
        "summary":          summary,
        "skill_gap":        skill_gap,
        "recommendations":  recommendations,
    }