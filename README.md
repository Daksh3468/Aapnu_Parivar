# Aapnu Parivar (આપણું પરિવાર)
### Unified Gujarat Household Identity & Welfare Beneficiary Gateway

Aapnu Parivar is an end-to-end digital government portal designed for Gujarat State to deliver single-window entitlement access across state and central welfare schemes with automated rules evaluation, paperless document verification, and full lifecycle tracking (births, deaths, and household division splits).

---

## 🚀 Key Features

1. **Unified Common Login Portal**:
   - Single sign-in portal supporting 10-digit Citizen Mobile Numbers and Official Officer Email accounts (`admin@gujarat.gov.in`).
   - Intelligent automated role-based routing (Citizens $\rightarrow$ `/my-family`, Department Officers $\rightarrow$ `/officer`).

2. **Structured 12-Digit Gujarat Family ID**:
   - Issues structured 12-digit Verhoeff-protected Family IDs (`GJ-DD-YY-SSSSSSS-C`).
   - Prominently displayed across citizen and officer dashboards.

3. **Automated Rules & Entitlement Engine**:
   - Evaluates citizen eligibility across welfare schemes using verified income bands, ration card types, land holdings, social categories, and document status.

4. **Household Division & Lineage Split Engine**:
   - 4-Step wizard allowing citizens to divide households when establishing independent nuclear families.
   - Calculates real-time Anomaly Risk Scores (0–100); low-risk splits ($\le 50$) auto-approve with new Family IDs, while high-risk splits route to officer review queues.

5. **Aapnu Mitra AI Welfare Assistant**:
   - Floating AI chatbot widget offering instant guidance on scheme eligibility, family splits, Family IDs, and document vault status.

6. **Departmental Console & Analytics**:
   - Officer jurisdiction scoping (State, District, Taluka) for document verification, split request reviews, and DBT benefit simulation projections.

---

## 🛠️ Tech Stack

- **Frontend**: React, TypeScript, Vite, TailwindCSS, TanStack Query, Lucide Icons
- **Backend**: Python, FastAPI, SQLAlchemy, Pydantic V2, Argon2 / Passlib, Pytest
- **Database**: SQLite (Development) / PostgreSQL (Production ready)

---

## 🚀 Local Development Setup

### 1. Backend Setup (FastAPI)
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m app.seed.synthetic_generator  # Seed 150+ synthetic Gujarat households
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🌐 Deployment Options

### Option A: Render (Full Stack Deployment - Recommended)
1. Fork or push this repository to GitHub: `https://github.com/Daksh3468/Aapnu_Parivar.git`.
2. **Backend Web Service**:
   - Create a new **Web Service** on [Render](https://render.com).
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. **Frontend Static Site**:
   - Create a new **Static Site** on Render connected to `frontend/`.
   - Build Command: `npm run build`
   - Publish Directory: `dist`

### Option B: Docker Container Deployment
```bash
docker-compose up --build
```
