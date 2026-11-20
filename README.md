# CivicPulse AI

> **Intelligent Urban Infrastructure Grievance Redressal and Municipal Operations Platform**

CivicPulse AI is a full-stack civic-tech platform designed to modernize citizen grievance logging, automated triaging, visual diagnostics, and municipal departmental workflows. By integrating geospatial tracking, severity prioritization, and Community Impact Scoring, CivicPulse AI bridges the communication gap between citizens and local governance authorities.

---

## 📌 Problem Statement & Solution

### The Problem
Traditional municipal grievance portals suffer from critical operational bottlenecks:
- **Unstructured Submissions:** Citizens submit vague descriptions without verified GPS coordinates, departmental classification, or photographic evidence.
- **Triage Delay:** Municipal departments manually sort complaints, delaying urgent interventions (e.g., severe potholes, water main bursts, exposed live wires).
- **Zero Visibility:** Citizens receive generic ticket IDs without real-time status updates, SLA progress, or verification audit trails.
- **Fragmented Resource Allocation:** Field teams lack geographic heatmaps and ward-level intelligence, leading to redundant dispatches and uncoordinated repairs.

### The Solution
CivicPulse AI provides a cohesive, end-to-end civic intelligence solution:
- **Guided Grievance Submission:** Multi-category selector, interactive OpenStreetMap / GPS location tagging, and multi-file drag-and-drop evidence uploads.
- **Automated Diagnostic & Impact Scoring:** Computes a 5-factor Community Impact Score to prioritize high-risk, high-density public hazards automatically.
- **Interactive Geospatial Visualization:** Real-time Civic Issues Map and Ward Explorer visualizing issue clusters, severity levels, and ward-specific resolution rates.
- **Municipal Admin Cockpit:** Unified dashboard for triage officers to update complaint statuses, assign field engineers, review resolution SLAs, and coordinate across municipal departments.

---

## 🎯 Project Objectives

1. **Empower Citizens:** Provide an intuitive interface to submit, track, and verify civic grievances with sub-second responsiveness.
2. **Accelerate Response Times:** Provide automated department routing (Roads, Water, Sanitation, Electrical, Drainage, Planning) with estimated resolution windows (24–72 hours).
3. **Data-Driven Urban Planning:** Aggregate ward-level metrics and impact scores to assist city planners in identifying recurring infrastructure vulnerabilities.
4. **Transparent Governance:** Implement verifiable stage-by-stage audit timelines from submission through inspection to final resolution.

---

## 🚀 Key Features

### Citizen Portal
- **Secure Authentication:** Register and log in using email/password with bcrypt hashing and JWT token exchange (access & refresh tokens).
- **Incident Reporting Form:** Submit grievances with category classification, dynamic description character counter (500-char limit), ward selection, and geolocation tagging.
- **Evidence Upload:** Attach photographic evidence (JPG, PNG, WebP) with client-side preview, validation, and file removal controls.
- **Track Complaints:** Filterable overview showing personal complaints and community-wide issues with status badges (*Submitted*, *Under Review*, *In Progress*, *Resolved*, *Rejected*).
- **Complaint Timeline & Audit Trail:** Detailed timeline showing timestamped milestones (Submission → AI Triage → Department Assignment → Field Repair → Verified Resolution).

### Spatial & Analytics Modules
- **Civic Issue Map:** Interactive Leaflet map rendering color-coded pins based on severity (Critical, High, Medium, Low), with popup previews and real-time category/status filters.
- **Ward Explorer:** Interactive zonal dashboard loading municipal wards with complaint counts, resolution rates, and automated map panning to ward centerpoints.
- **Community Impact Score (CIS):** Explainable composite metric weighting:
  $$\text{CIS} = (\text{Severity} \times 0.35) + (\text{Reach} \times 0.25) + (\text{Proximity} \times 0.20) + (\text{Duration} \times 0.10) + (\text{Corroboration} \times 0.10)$$

### Municipal Administration
- **Admin Cockpit:** Real-time KPI summaries (Total, Submitted, Under Review, In Progress, Resolved, Rejected, High Priority).
- **Priority Redressal Queue:** Filterable data table enabling quick status transitions and field inspector assignments.
- **Department Registry:** Contact and operational information for 6 municipal departments (Roads & Infrastructure, Sanitation & SWM, Water Supply & Sewerage, Street Lighting & Electrical, Drainage, Town Planning).

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Zustand (State Management), React Router v6 |
| **Mapping & Geospatial** | Leaflet, React-Leaflet, OpenStreetMap Tile Layers |
| **Backend** | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async ORM), aiosqlite |
| **Authentication & Security** | OAuth2 Password Bearer, Passlib (bcrypt 4.0.1), python-jose (JWT), CORS Middleware |
| **Database** | SQLite with WAL mode (Development) / PostgreSQL compatible (Production) |
| **AI / Diagnostics** | Deterministic rule-based triage pipeline with Google Gemini 2.0 Flash integration hooks |

---

## 📂 System Architecture & Directory Structure

```text
civic.ai/
├── .gitignore                      # Git exclusion rules for secrets, DBs, and builds
├── README.md                       # Comprehensive project documentation
├── backend/
│   ├── .env.example                # Backend environment configuration template
│   ├── requirements.txt            # Python dependencies
│   ├── test_full_api.py            # Comprehensive 24-point automated test suite
│   ├── app/
│   │   ├── main.py                 # FastAPI application factory, CORS, and startup lifespan
│   │   ├── core/
│   │   │   ├── config.py           # Pydantic BaseSettings management
│   │   │   └── security.py         # Passlib bcrypt hashing and JWT token handlers
│   │   ├── db/
│   │   │   └── base.py             # Async engine, sessionmaker, and table lifecycle
│   │   ├── models/                 # SQLAlchemy 2.0 ORM models (User, Complaint, etc.)
│   │   ├── schemas/                # Pydantic request/response validation schemas
│   │   ├── services/               # Complaint, audit, file, and notification business logic
│   │   └── api/v1/
│   │       ├── dependencies.py     # OAuth2 auth dependencies and role guards
│   │       └── endpoints/
│   │           ├── auth.py         # /register, /login, /token, /refresh, /me
│   │           └── complaints.py   # CRUD, /stats, /wards, /departments, /ai-analysis, /timeline
└── frontend/
    ├── .env.example                # Frontend environment configuration template
    ├── package.json                # Node.js dependencies and build scripts
    ├── tsconfig.json               # TypeScript compiler configuration
    ├── vite.config.ts              # Vite bundler configuration
    ├── index.html                  # HTML entry point
    └── src/
        ├── App.tsx                 # App router and authenticated PrivateRoute guards
        ├── main.tsx                # React DOM root initialization
        ├── index.css               # Global styles and Tailwind directives
        ├── store/
        │   └── auth.ts             # Zustand store for user session and JWT storage
        ├── components/
        │   └── Layout.tsx          # Responsive navigation sidebar, topbar, and impact gauge
        └── pages/
            ├── Login.tsx           # Authentication screen with demo quick-fill
            ├── Register.tsx        # Citizen account registration form
            ├── Dashboard.tsx       # KPI metrics and user activity dashboard
            ├── SubmitComplaint.tsx # 2-column grievance submission matching reference UI
            ├── TrackComplaints.tsx # Filterable complaint status tracker
            ├── ComplaintDetail.tsx # Detailed grievance diagnostics and audit timeline
            ├── CivicMap.tsx        # Interactive Leaflet issue map
            ├── WardMap.tsx         # Ward Explorer with aggregated statistics
            ├── AdminDashboard.tsx  # Municipal administrative priority queue
            └── Departments.tsx     # Municipal service directory
```

---

## ⚙️ Installation Prerequisites

Before setting up the project locally, ensure you have:
1. **Python 3.12+**: Verify via `python --version` or `py -3.12 --version`.
2. **Node.js 18+ & npm**: Verify via `node -v` and `npm -v`.
3. **Git**: Installed and configured on your machine.

---

## 🚀 Step-by-Step Local Setup

### 1. Clone the Repository
```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd civic.ai
```

### 2. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python 3.12 virtual environment:
   - **Windows (PowerShell):**
     ```powershell
     python -m venv venv312
     .\venv312\Scripts\Activate.ps1
     ```
   - **Linux / macOS:**
     ```bash
     python3.12 -m venv venv
     source venv/bin/activate
     ```
3. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   *(Review `.env` and configure custom keys as needed. The application includes safe defaults for local SQLite development).*

5. Start the FastAPI backend:
   ```powershell
   .\venv312\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   - Health Check: `http://127.0.0.1:8000/api/v1/health`
   - Interactive Swagger Docs: `http://127.0.0.1:8000/docs`

---

### 3. Frontend Setup
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Configure frontend environment variables:
   ```bash
   cp .env.example .env
   ```
   *(Ensure `VITE_API_URL=http://127.0.0.1:8000` is set).*

4. Start the Vite development server:
   ```bash
   npm run dev
   ```
   - Open your browser at `http://localhost:5173`.

---

## 🔐 Environment Variables

### Backend (`backend/.env`)
| Variable | Description | Default / Example Placeholder |
|---|---|---|
| `APP_NAME` | Display name of the application | `CivicPulse AI` |
| `APP_ENV` | Application environment (`development` / `production`) | `development` |
| `DEBUG` | FastAPI debug mode flag | `true` |
| `API_PREFIX` | Prefix for versioned REST routes | `/api/v1` |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed CORS origins | `http://localhost:5173,http://localhost:3000` |
| `DATABASE_URL` | Async database connection URL | `sqlite+aiosqlite:///./civicpulse.db` |
| `SECRET_KEY` | 32-byte secret for JWT signing | `<GENERATE_A_RANDOM_SECRET_KEY>` |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| Access token lifetime in minutes | `60` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime in days | `7` |
| `GEMINI_API_KEY` | Google Gemini API Key (optional) | `<YOUR_GEMINI_API_KEY>` |
| `DEMO_MODE` | Enable deterministic fallbacks when API keys are absent | `true` |
| `SUPER_ADMIN_EMAIL` | Default admin email seeded on initialization | `admin@civicpulse.ai` |
| `SUPER_ADMIN_PASSWORD` | Default admin password seeded on initialization | `CivicAdmin123!` |

### Frontend (`frontend/.env`)
| Variable | Description | Default / Example Placeholder |
|---|---|---|
| `VITE_API_URL` | Backend URL for API calls | `http://127.0.0.1:8000` |

---

## 📡 API Reference

### Authentication Endpoints
- `POST /api/v1/auth/register` — Register a new citizen account (`UserPublic` response).
- `POST /api/v1/auth/login` — JSON credential exchange returning access and refresh JWTs.
- `POST /api/v1/auth/token` — OAuth2 standard form-encoded authentication endpoint.
- `POST /api/v1/auth/refresh` — Refresh expired access token using Bearer refresh token.
- `GET /api/v1/auth/me` — Return current authenticated user profile (`Authorization: Bearer <token>`).

### Complaints & Diagnostics Endpoints
- `POST /api/v1/complaints/` — Submit a new grievance record.
- `GET /api/v1/complaints/` — List complaints with pagination, category, priority, and status filters.
- `GET /api/v1/complaints/my` — Return complaints filed by the authenticated user.
- `GET /api/v1/complaints/stats` — Return aggregate complaint statistics.
- `GET /api/v1/complaints/wards` — Return aggregated statistics and geo-coordinates per ward.
- `GET /api/v1/complaints/departments` — List municipal departments and contacts.
- `GET /api/v1/complaints/{id}` — Retrieve detailed record of a single complaint.
- `PATCH /api/v1/complaints/{id}` — Update complaint status, priority, or officer assignment.
- `POST /api/v1/complaints/upload` — Upload image evidence file (multipart/form-data).
- `GET /api/v1/complaints/{id}/ai-analysis` — Return AI diagnostics, severity, and CIS breakdown.
- `GET /api/v1/complaints/{id}/timeline` — Return audit trail milestones for a complaint.

---

## 🧪 Testing

The repository includes a comprehensive 24-point automated test script verifying health, user registration, duplicate prevention, form/JSON logins, invalid password rejection, complaints CRUD, ward aggregation, and permissions.

To execute the test suite against a running backend:
```powershell
cd backend
.\venv312\Scripts\python.exe -u test_full_api.py
```

To run the frontend TypeScript type check and production build:
```bash
cd frontend
npx tsc --noEmit
npm run build
```

---

## 🚢 Deployment Guidelines

### Frontend on Vercel
1. Link your GitHub repository to [Vercel](https://vercel.com).
2. Set the **Root Directory** to `frontend`.
3. Configure Build Settings:
   - **Framework Preset:** `Vite`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Add Environment Variable:
   - `VITE_API_URL` = `<YOUR_RENDER_BACKEND_URL>`
5. Deploy.

### Backend on Render
1. Create a **New Web Service** on [Render](https://render.com) linked to your repository.
2. Set the **Root Directory** to `backend`.
3. Configure Service Settings:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Configure Environment Variables in the Render Dashboard:
   - `APP_ENV` = `production`
   - `DEBUG` = `false`
   - `SECRET_KEY` = `<GENERATE_A_32_BYTE_RANDOM_SECRET>`
   - `ALLOWED_ORIGINS` = `https://<YOUR_VERCEL_APP_DOMAIN>.vercel.app`
   - `DATABASE_URL` = `<YOUR_POSTGRESQL_CONNECTION_STRING>` *(Render PostgreSQL)*
5. Deploy.

---

## 🔒 Security Considerations

- **Zero Secret Ingestion:** All sensitive keys, JWT tokens, and database passwords are loaded strictly from environment variables. `.gitignore` completely excludes `.env` and local database files from Git tracking.
- **Password Protection:** All user passwords are encrypted using `bcrypt` (Passlib 4.0.1 compatible). Passwords are never stored in plaintext or logged.
- **JWT Protection:** Access tokens expire within 60 minutes. Cryptographic token decoding enforces algorithm constraints (`HS256`).
- **Role-Based Access Control (RBAC):** Administrative endpoints require specific role dependencies (`ADMIN`, `SUPERVISOR`, `DEPARTMENT_OFFICER`).
- **Input Sanitization:** String inputs and geographic bounds are sanitized and constrained via Pydantic validators.

---

## 🖼️ Application Screenshots

| Citizen Submission Screen | Interactive Issue Map |
|:---:|:---:|
| ![Submit Grievance](docs/screenshots/submit_complaint.png) <br> *(Placeholder: Grievance submission with drag-and-drop and map)* | ![Civic Map](docs/screenshots/civic_map.png) <br> *(Placeholder: Leaflet issues map with priority markers)* |

| Explore Ward Map | Municipal Admin Cockpit |
|:---:|:---:|
| ![Ward Explorer](docs/screenshots/ward_explorer.png) <br> *(Placeholder: Ward metrics and resolution percentages)* | ![Admin Dashboard](docs/screenshots/admin_dashboard.png) <br> *(Placeholder: Priority queue and triage management)* |

---

## 🔮 Future Enhancements

- **Vector-Based Deduplication:** Integrate pgvector / ChromaDB for visual and textual semantic similarity deduplication across complaints.
- **Real-Time Push Notifications:** Add WebSockets and WebPush notifications for immediate status alerts to citizens.
- **Municipal Work-Order Mobile App:** Offline-first progressive web app for field engineers conducting on-site verifications.
- **Multilingual Voice Triage:** Native speech-to-text input supporting regional Indian languages (Kannada, Hindi, Tamil).

---

## 🤝 Contribution Guidelines

1. Fork the Project repository.
2. Create your Feature Branch (`git checkout -b feature/NewFeature`).
3. Commit your changes with clear messages (`git commit -m 'feat: Add NewFeature'`).
4. Push to the Branch (`git push origin feature/NewFeature`).
5. Open a Pull Request.

---

## 📄 License

This project is currently developed and maintained as an open civic technology initiative. A formal open-source license (such as MIT or Apache 2.0) may be selected prior to public distribution.
