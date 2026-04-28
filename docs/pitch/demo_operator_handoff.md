# Demo video operator handoff

Give this document to whoever records the NyayaLens demo. They do not need prior context on the codebase. Follow sections in order the first time through.

---

## 1. What you are demonstrating

NyayaLens is a web app plus API:

1. User creates a **project**.
2. User uploads a **CSV dataset** (or you rely on defaults server-side).
3. User starts an **audit** that runs fairness metrics and mitigation in the backend.
4. User opens an **AI report** (Gemini when an API key is set; fallback text otherwise).

You need **two terminals** locally: one for the Python API, one for Flutter Web in Chrome.

---

## 2. Software you must install first

Install these before cloning the repo:

| Tool | Why |
|------|-----|
| **Git** | Clone `https://github.com/Deltasthicc/google-hacks` |
| **Python 3.11 or 3.12** | Runs the FastAPI backend |
| **Flutter SDK** (stable channel, Web enabled) | Runs the Flutter web app |

Optional but recommended:

| Tool | Why |
|------|-----|
| **VS Code or Cursor** | Edit `.env` or skim logs |

Verify installs:

```powershell
git --version
python --version
flutter doctor
```

Fix anything `flutter doctor` marks as blocking for **Chrome** / **Web**.

---

## 3. Clone and folder layout

```powershell
cd %USERPROFILE%\Documents
git clone https://github.com/Deltasthicc/google-hacks.git
cd google-hacks
```

Important folders:

| Path | Role |
|------|------|
| `backend/` | FastAPI service |
| `frontend/flutter_app/` | Web UI |
| `ml/datasets/demo/` | Ready-made CSVs for demos (`lending_mini_demo.csv`, `hiring_mini_demo.csv`) |

---

## 4. Backend terminal (Terminal A)

Always run API commands **from `backend/`**.

### 4.1 Virtual environment (recommended)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
```

Every new terminal session:

```powershell
cd backend
.\.venv\Scripts\activate
```

### 4.2 Install dependencies

You need **both** requirement files so audits run the ML pipeline:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-ml.txt
```

Do **not** skip `requirements-ml.txt`. Audits fail silently into placeholders without Fairlearn or the bundled ML stack.

### 4.3 Environment variables (optional but important for Gemini)

For **real Gemini narratives** in reports:

```powershell
$env:GEMINI_API_KEY="paste-your-key-here"
```

Get a key from Google AI Studio (`https://aistudio.google.com/apikey`). Without this variable the API still runs but reports use deterministic fallback wording instead of Gemini prose.

Keep **Firebase strict mode off** for local demos unless you have real Firebase tokens:

```powershell
$env:FIREBASE_STRICT="false"
```

Unset strict mode if unsure:

```powershell
Remove-Item Env:FIREBASE_STRICT -ErrorAction SilentlyContinue
```

BigQuery (`GOOGLE_CLOUD_PROJECT`) is optional for recording the UI flow.

### 4.4 Start the server

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
```

Leave this terminal **open**.

Sanity checks in a browser:

- `http://127.0.0.1:8080/health` should return JSON with status OK.
- `http://127.0.0.1:8080/docs` shows Swagger UI.

### 4.5 Stop the server

Press **Ctrl+C** in Terminal A.

---

## 5. Flutter terminal (Terminal B)

Open a **second** terminal.

### 5.1 Dependencies

```powershell
cd frontend\flutter_app
flutter pub get
```

### 5.2 Run Web pointed at local API

```powershell
flutter run -d chrome --dart-define=API_BASE_URL=http://127.0.0.1:8080
```

Chrome opens automatically. Wait until the app loads without red error banners.

### 5.3 Stop Flutter

Press **q** in the Flutter terminal or close Chrome if needed.

---

## 6. Recommended order when recording

1. Start **Terminal A** (backend), confirm `/health`.
2. Start **Terminal B** (Flutter).
3. In the browser: create a **project**, note its name (looks calm on camera).
4. Go to **Upload** (or equivalent flow): upload **`ml/datasets/demo/lending_mini_demo.csv`** from disk using **Browse**.
   - Target column: **`approved`**
   - Sensitive columns: **`gender`**
5. Run **model audit** or **data audit** as the UI exposes it (paths align with audit endpoints).
6. Wait until audit finishes (`completed` style status).
7. Open **Reports** or **Generate report**, pick **Executive** then **Technical** if both exist.
8. If you showed numbers, optionally open **Swagger** `/docs` only if the video needs a power-user shot; most judges only need the product UI.

---

## 7. What not to do

| Do not | Why |
|--------|-----|
| Run `pip install` only on `requirements.txt` and skip `requirements-ml.txt` | ML audit path breaks or degrades. |
| Run two backends on **port 8080** | Second process fails or hijacks traffic. |
| Paste **API keys** into Discord, stream, or commit to Git | Keys get scraped; rotate if leaked. |
| Set `FIREBASE_STRICT=true` without a real Firebase login | Every API call returns 401 and the UI looks broken. |
| Rehearse on a flaky guest Wi‑Fi for the first time | First `OpenML` fetch for Adult dataset can stall; prefer **bundled demo CSVs** for the video. |
| Move the CSV to a path with Unicode edge cases | Stay under a simple path like `Documents\google-hacks\...` |
| Close Terminal A before finishing the scene | Flutter calls fail mid-take. |

---

## 8. If something fails

| Symptom | Check |
|---------|--------|
| Flutter says connection failed | Backend still running? Correct `API_BASE_URL`? Firewall blocking localhost? |
| 404 on audits | Did you create a project first? |
| Report is generic boilerplate | `GEMINI_API_KEY` missing; set it and regenerate. |
| Audit stuck or error | Read Terminal A traceback; confirm `requirements-ml.txt` installed. |
| OpenML hangs | Switch to **`lending_mini_demo.csv`** which needs no internet. |

---

## 9. Filming hygiene

- **1080p** screen capture minimum.
- **Mute** system sounds; voiceover only.
- **Do not** show real API keys on screen when setting environment variables (set them before you hit Record, or blur the line in post).
- Use a **clean browser profile** or hide bookmark bar and unrelated tabs.

---

## 10. After recording

Export **unlisted YouTube**, put the link in the team submission sheet and in `docs/submission/project_links.md` when the team updates it.

---

## 11. Hosted demo (optional, not required to read first)

If the product is deployed to Firebase Hosting + Cloud Run, build Flutter with the **production** API URL instead of localhost. That is a separate deploy step coordinated with the team; the local recipe above is enough for a valid submission video as long as everything on screen is real.
