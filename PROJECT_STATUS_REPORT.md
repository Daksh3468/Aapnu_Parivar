# Aapnu Parivar (આપણું પરિવાર) — Project Status Report & Roadmap

**Date & Time**: September 20, 2026  
**Project**: Aapnu Parivar — Flagship Family Registry & Unified Welfare Entitlement Portal  
**Target Region**: Government of Gujarat, India  
**Design Standard**: Official Gujarat Government Portal Style (Minimal, Professional, Light Mode)

---

## 1. Executive Summary

**Aapnu Parivar** is a unified family registry and welfare entitlement platform built for the Government of Gujarat. It aggregates citizen demographic profiles, household compositions, income bands, land records, and verified identity documents into a single authoritative registry. The platform automatically maps households to eligible state and central welfare schemes, eliminating manual paperwork and fragmented portal applications.

### Technology Stack & Architecture
- **Backend Framework**: Python FastAPI (REST API v1)
- **Database Layer**: SQLite (SQLAlchemy 2.0 ORM with Foreign Key constraints and indexed queries)
- **Frontend Stack**: React 18 + TypeScript + Vite + Tailwind CSS + Lucide Icons + TanStack Query
- **Security & Access Control**: JWT Bearer Authentication, Argon2 password hashing, OTP challenge lifecycle, Role-Based Access Control (RBAC), and Officer District Jurisdiction Scoping
- **Testing & Quality Assurance**: Automated unit testing (`pytest`) and strict TypeScript compilation (`tsc & vite build`)

---

## 2. Comprehensive Summary of Completed Work (Phases 1 to 7)

### Phase 1: Foundation & Official Design System ✅
- **Official Government UI System**: Implemented clean, minimal light-mode styling inspired by official Gujarat Government portals (`#0f172a` Navy, `#d97706` Saffron, `#059669` Emerald Green). Integrated official tricolor header stripes and state emblem branding.
- **Base Infrastructure**: Configured FastAPI backend structure, CORS policies, environment configurations, SQLite database connection, and frontend Vite setup.
- **Health System API**: Created `/api/v1/health` API reporting system status, database connectivity, environment mode, and system timestamp.

### Phase 2: Master Scheme Catalog & Live Sync Engine ✅
- **Scheme & Category Models**: Designed `SchemeCategory` and `Scheme` tables with support for central (`CENTRAL`) and state (`GUJARAT_STATE`) schemes.
- **Live Connector Services**: Built `MockCentralPortalConnector` and `MockGujaratPortalConnector` to simulate real-time API integrations with external government portals (Digital Gujarat, MyScheme).
- **Automated Catalog Synchronization**: Developed background sync service to fetch, update, and validate scheme metadata, funding splits, and eligibility rules.
- **Citizen Scheme Explorer UI**: Created `AllSchemesPage.tsx` with multi-filter search (by department, target group, funding type, and level).

### Phase 3: Authentication & Multi-Role Access System ✅
- **User Account & Role Hierarchy**: Built `UserAccount` model supporting `CITIZEN_HEAD`, `CITIZEN_MEMBER`, `DISTRICT_OFFICER`, `STATE_ADMIN`, and `SYSTEM_AUDITOR`.
- **Security Protocols**: Argon2id password hashing and JWT access/refresh token generation.
- **Mobile OTP Challenge Engine**: Simulated 6-digit OTP delivery with 5-minute expiry window, failure rate limiting, and single-use challenge consumption.
- **Authentication Pages**: Built responsive citizen and officer login components (`LoginPage.tsx`, `OfficerLoginPage.tsx`, `DemoOtpBanner.tsx`).

### Phase 4: Family Registry & Member Management ✅
- **Household Registry Engine**: Implemented `Family`, `Person`, and `FamilyMember` schema with unique `GJ-FAM-YYYY-XXXXXX` ID generation.
- **Demographic & Address Profiles**: Stored district codes, taluka, village/town, pincode, ration card categories (BPL, APL-1, APL-2, AAY), and annual household income bands.
- **Multi-Step Household Registration**: Built interactive 4-step registration wizard (`RegisterStepper.tsx`, `FamilyIdInput.tsx`) allowing citizens to register household head, address, and family members.
- **Citizen Profile Dashboard**: Created `FamilyProfilePage.tsx` displaying household identity card, member rosters, and status indicators.

### Phase 5: Aadhaar Verification & e-KYC Integration ✅
- **Verhoeff Algorithm Validation**: Implemented client & server-side Aadhaar checksum validation enforcing synthetic Aadhaar numbers starting with `1`.
- **Demographic e-KYC Verification**: Created e-KYC verification service (`verification_service.py`) comparing Aadhaar demographic records against registered family members.
- **Interactive Member Verification Modal**: Built `VerifyMemberModal.tsx` for citizens to verify unlinked household members via Aadhaar e-KYC OTP validation.

### Phase 6: Officer Portal, District Jurisdiction & Audit Trail ✅
- **Jurisdiction Filter Engine**: Built `build_officer_jurisdiction_scope()` and `apply_family_jurisdiction_filter()` in `jurisdiction.py`, restricting district officers strictly to households within assigned district codes (`district_id`).
- **Audit Logging Subsystem**: Built immutable `AuditLog` table and `write_audit()` logger tracking all system actions (logins, verification, document uploads, reviews) with timestamp and actor ID.
- **Officer Dashboard Console**: Developed `OfficerHome.tsx` featuring real-time KPI metrics (registered families, verified members, pending confirmations, duplicate flags).

### Phase 7: Document Vault, Eligibility Engine & Confirmation Queue ✅
- **Digital Document Vault**: Built `Document` model and API endpoints (`/api/v1/families/{id}/documents`) supporting income certificates, caste certificates, land records, domicile proofs, and disability cards.
- **Automated Scheme Eligibility Engine**: Developed `EligibilityEngine` evaluating household attributes against scheme rule specs (income caps, land holding limits, age criteria, social category, unorganized worker status, required documents).
- **Citizen Vault & Entitlements UI**: Built `DocumentVaultSection.tsx` and `SchemeEligibilitySection.tsx` with expandable *"Why Am I Eligible / Ineligible?"* breakdown drawers detailing passed rules, failed criteria, and missing document requirements.
- **Officer Review & Override Queue**: Created `OfficerReviewQueue.tsx` allowing department officers to review pending document vault uploads and execute manual eligibility overrides with notes.

### Phase 8: Application Tracking & Official Portal Interop ✅
- **Scheme Application Lifecycle**: Added household-scoped `SchemeApplication` and append-only status-history models with `SUBMITTED → UNDER_REVIEW → APPROVED → DISBURSED / REJECTED` states.
- **One-Click Eligible Application**: Household heads can submit pre-filled applications only for eligible schemes; a database constraint prevents duplicate active applications for the same household and scheme.
- **Portal Simulation & Tracking**: Added protected application list and refresh endpoints that use the existing mock Digital Gujarat/Central portal adapters and generate synthetic `DG-`/`JS-` references. The citizen profile now contains an Applications tab with timeline and official-link access.
- **Risk Fixes Delivered**: Unassigned officers are denied access rather than granted statewide scope; production refuses default secrets/demo schema creation; Alembic baseline migration support and a project README are included; the invalid OTP error path and eligibility age calculation are corrected; fuzzy duplicate flags are now generated at registration and can be resolved through officer APIs.

---

## 3. Current System Verification & Metrics

- **Backend Test Suite**: **36 / 36** unit tests passing (`python -m pytest`) with 100% assertion success rate across Auth, Domain, Family, Health, Verification, Schemes, Eligibility, Applications, Duplicates, and Life Events.

- **Frontend Production Build**: **0 TypeScript errors**, clean bundle build (`npm run build` via Vite).
- **Alembic Database Status**: Baseline migration `20260920_01 (head)` verified and applied successfully.
- **Design Aesthetic Compliance**: Clean minimal light mode, official typography, government color palette (`#0f172a` Navy, `#d97706` Amber/Saffron, `#059669` Emerald Green), responsive UI layout.

---

## 4. Phase 10 Completion — Statewide Analytics Dashboard & DBT Simulation ✅

### What Was Delivered in Phase 10

#### Backend
| Component | File | Description |
|---|---|---|
| Analytics Model | `backend/app/models/analytics.py` | `AnalyticsDailySnapshot` + `DisbursementSimulationRun` SQLAlchemy models |
| Analytics Service | `backend/app/services/analytics_service.py` | Snapshot refresh, district breakdown, monthly trend, simulation engine |
| Analytics API | `backend/app/api/v1/analytics.py` | 5 new endpoints: `/overview`, `/refresh`, `/simulate`, `/simulations`, `/simulations/{id}` |
| Tests | `backend/tests/test_analytics.py` | 15 new tests covering service + API (auth, RBAC, data integrity) |

#### Frontend
| Component | File | Description |
|---|---|---|
| Dashboard Page | `frontend/src/pages/AnalyticsDashboardPage.tsx` | Full statewide KPI dashboard with 7 charts |
| Route | `frontend/src/App.tsx` | `/analytics` route added |
| Navigation | `frontend/src/components/Navbar.tsx` | "Analytics" link with BarChart2 icon |

#### Analytics Dashboard Features
- **KPI Cards** (7): Total Households, Total Members, Total Disbursed, Applications, Births, Deaths, Splits
- **Monthly Trend Chart** (dual-axis line): Applications vs Disbursement over 12 months
- **Application Status Pie Chart**: Approved / Disbursed / Pending / Rejected breakdown
- **District Breakdown Bar Chart**: Households per district with multi-color palette
- **Top Schemes Horizontal Bar Chart**: Ranked by application volume
- **DBT Simulation Panel**: Officer-triggered simulations with label, per-household amount, scheme/income/ration filters
- **Simulation History Table**: All past runs with Run ID, eligible count, projected total, status

#### RBAC for Analytics
| Endpoint | Minimum Role |
|---|---|
| `GET /analytics/overview` | Public (no auth required) |
| `POST /analytics/refresh` | FIELD_OFFICER+ |
| `GET /analytics/simulations` | FIELD_OFFICER+ |
| `POST /analytics/simulate` | DISTRICT_OFFICER+ |
| `GET /analytics/simulations/{id}` | FIELD_OFFICER+ |

---

## 5. Final System Metrics (Phase 10 Complete)

| Metric | Value |
|---|---|
| Backend tests passing | **51 / 51** ✅ |
| Frontend TypeScript errors | **0** ✅ |
| API routes total | **40+** across 12 routers |
| Frontend pages | **8** (Citizen Home, Family Profile, All Schemes, Login, Officer Login, Register, Officer Dashboard, Analytics) |
| Frontend components | **15** |
| Database models | **18** SQLAlchemy models |
| Phases completed | **10 / 10** 🎉 |

---

## 6. Remaining Hardening (Future Work)

- Replace `datetime.utcnow()` with `datetime.now(datetime.UTC)` across all services (non-breaking `DeprecationWarning` only)
- Add Alembic migration scripts for all new tables (currently using `AUTO_CREATE_SCHEMA=true` in dev)
- Add `Dockerfile` + `docker-compose.yml` for containerised deployment
- Add `Scheme.max_annual_benefit_inr` monetary field to enable real disbursement financial tracking
- Implement CSV export endpoint for analytics data
- Configure HTTPS, rate limiting, and WAF for production deployment

---

*This report reflects the complete, final state of the Aapnu Parivar platform after Phase 10.*
