# Aapnu Parivar (આપણું પરિવાર)
### Unified Gujarat Household Identity & Welfare Beneficiary Gateway

> **One Family. One ID. Every Benefit.**

**Aapnu Parivar** is an enterprise-grade digital government platform engineered for Gujarat State to deliver single-window entitlement access across state and central welfare schemes. By shifting benefit eligibility from individual silos to a verified household identity, Aapnu Parivar eliminates duplicate beneficiaries, prevents welfare exclusion, automates document verification, and gracefully handles complex real-world family changes (such as household division splits, births, and marriages) with complete lineage retention.

---

## 🌟 Executive Summary & Problem Vision

Every welfare scheme in Gujarat traditionally maintains its own beneficiary database, forcing citizens to re-submit identical identity and income documents repeatedly. This creates three critical bottlenecks:
1. **Exclusion Gap**: Eligible citizens miss out on benefits due to fragmented scheme awareness.
2. **Duplicate & Leakage Errors**: Ineligible individuals or duplicated records inflate state expenditure.
3. **Fragmented Household Visibility**: Neither citizens nor department officers have a single dashboard showing complete household entitlements.

**Aapnu Parivar** solves these challenges by establishing a single, verified **12-Digit Gujarat Family ID** (`GJ-DD-YY-SSSSSSS-C`) protected by the Verhoeff checksum algorithm.

---

## 🏗️ 1. System Architecture

The system is built on a clean 3-tier architecture with role-based security, modular API endpoints, declarative rule evaluations, and synthetic data generation.

### 1.1 High-Level Architecture Diagram
```mermaid
flowchart TB
  subgraph CLIENT["Client layer (React)"]
    CW["Citizen web app"]
    OW["Officer and admin dashboard"]
  end

  subgraph BACKEND["Backend (FastAPI, Python)"]
    API["API layer: routers, auth, RBAC, jurisdiction filter"]
    AUTHS["Auth service: password, OTP, tokens"]
    FAMS["Family and membership service"]
    VERS["Verification service"]
    DUPS["Duplicate detection service (rapidfuzz)"]
    EVTS["Life event service"]
    ELGS["Eligibility engine (YAML rules)"]
    SCHS["Scheme and application service"]
    CONN["Connector framework"]
    NOTS["Notification service"]
    AUDS["Audit and consent service"]
    ANAS["Analytics service"]
    AISS["AI stubs: chatbot, anomaly score"]
  end

  DB[("PostgreSQL / SQLite")]

  subgraph EXT["Original source systems (mocked in MVP)"]
    UID["Aadhaar e-KYC (mock)"]
    RAT["Ration card and NFSA (mock)"]
    DLK["Document locker (mock)"]
    SP1["Central scheme portals (mock)"]
    SP2["Gujarat scheme portals (mock)"]
    SMS["SMS / WhatsApp gateway (mock)"]
  end

  CW --> API
  OW --> API
  API --> AUTHS
  API --> FAMS
  API --> EVTS
  API --> SCHS
  API --> ANAS
  API --> AISS
  FAMS --> VERS
  FAMS --> DUPS
  EVTS --> FAMS
  EVTS --> ELGS
  FAMS --> ELGS
  ELGS --> SCHS
  SCHS --> CONN
  VERS --> CONN
  NOTS --> CONN
  CONN --> UID
  CONN --> RAT
  CONN --> DLK
  CONN --> SP1
  CONN --> SP2
  CONN --> SMS
  AUTHS --> DB
  FAMS --> DB
  DUPS --> DB
  EVTS --> DB
  ELGS --> DB
  SCHS --> DB
  AUDS --> DB
  ANAS --> DB
  FAMS --> AUDS
  EVTS --> NOTS
  ELGS --> NOTS
```

### 1.2 Execution Topology Diagram (Local & Containerized)
```mermaid
flowchart LR
  U["Browser: Citizen or Department Officer"] --> FE["Frontend (React + Vite + Tailwind CSS)"]
  FE --> BE["Backend API (FastAPI + SQLAlchemy)"]
  BE --> DB[("SQLite DB / PostgreSQL")]
  BE --> RULE["Rules Engine (Declarative YAML)"]
  BE --> AI["Aapnu Mitra Chatbot & Anomaly Engine"]
```

---

## 🚀 2. Core Functional Modules & User Flows

### 2.1 Unified Common Login Portal & Intelligent Role Routing
- **Dual-Mode Sign-In**: Supports sign-in via **10-Digit Citizen Mobile Number + Password** or **Gmail / Google Account OAuth (Simulated)**.
- **Unified Portal for Citizens & Officers**: Single portal handles both citizen families and government officials.
- **Intelligent Role-Based Routing**:
  - Official Department Emails (e.g. `admin@gujarat.gov.in`) automatically route to the **Departmental Officer Console** (`/officer`).
  - Family Mobile & Citizen logins automatically route to the **Citizen Family Portal** (`/my-family`).
- **First-Time Registration & Password Management**: Prompts first-time registrants to set up their password during family onboarding and enables authenticated password updates (`POST /api/v1/auth/password/change`).

### 2.2 Family & Membership Lifecycle
A family is tracked through an explicit state lifecycle ensuring only valid, verified households receive government benefits.

#### Family State Lifecycle Diagram
```mermaid
stateDiagram-v2
  [*] --> DRAFT: start registration
  DRAFT --> SUBMITTED: submit (Family ID issued)
  SUBMITTED --> VERIFIED: officer verifies
  SUBMITTED --> NEEDS_CORRECTION: officer requests changes
  NEEDS_CORRECTION --> SUBMITTED: family resubmits
  VERIFIED --> NEEDS_CORRECTION: correction or risky event
  VERIFIED --> SUSPENDED: fraud review
  SUSPENDED --> VERIFIED: cleared
  VERIFIED --> CLOSED: all members moved or deceased
  SUBMITTED --> CLOSED: rejected as invalid
  CLOSED --> [*]
```

#### Duplicate Person Prevention Flow Diagram
```mermaid
flowchart TD
  A["New or edited person"] --> B{"Aadhaar hash matches an existing person?"}
  B -- Yes --> C["Block. Show which action is needed: leave family, or join request"]
  B -- No --> D["Get blocked candidates: same DOB year, mobile or pincode"]
  D --> E["Score each candidate"]
  E --> F{"Best score"}
  F -- ">= 0.90" --> G["Block and open HIGH flag"]
  F -- "0.75 to 0.90" --> H["Allow as pending and open MEDIUM flag"]
  F -- "< 0.75" --> I["Proceed"]
  G --> J["Officer duplicate queue"]
  H --> J
  J --> K{"Officer decision"}
  K -- "Not duplicate" --> I
  K -- "Duplicate" --> L["Merge person records and keep history"]
  K -- "Needs info" --> M["Request correction from family"]
```

---

### 2.3 Household Division & Lineage Split Engine
When adult family members form independent nuclear households (e.g. upon marriage or economic division), citizens can initiate the 4-step **Family Split Wizard** (`FamilySplitWizardModal.tsx`):
1. **Select Moving Members**: Choose adult members and dependents leaving the original family.
2. **Nominate New Family Head**: Designate a verified adult to head the new household.
3. **Declare Address & Income**: Provide updated residential details, pincode, and household income band.
4. **Review & Automated Risk Assessment (0–100)**:
   - **Low Risk ($\le 50$)**: Immediate auto-approval with issuance of a new 12-Digit Verhoeff Family ID (`GJ-DD-YY-SSSSSSS-C`).
   - **High Risk ($> 50$)**: Formally submitted to the District Officer review queue.
   - Modal action buttons cleanly labeled **Close** for intuitive user navigation.
   - Preserves complete historical lineage records (`parent_family_id`, `child_family_id`).

#### Household Split Workflow Diagram
```mermaid
flowchart TD
  A["Adult member requests split"] --> B["Select members moving out and enter new address"]
  B --> C["Validate: adults verified, no pending event, all belong to source family"]
  C --> D["Compute anomaly score"]
  D --> E{"Score"}
  E -- "< 30" --> F["Auto-approve"]
  E -- "30 to 49" --> G["Auto-approve with flag for information"]
  E -- ">= 50" --> H["Officer review required"]
  H --> I{"Officer decision"}
  I -- Reject --> Z["Event rejected and requester notified"]
  I -- Approve --> F
  G --> F
  F --> J["Create new family and issue new Family ID"]
  J --> K["End old memberships and start new ones on the same date"]
  K --> L["Write lineage and family snapshots"]
  L --> M["Reassign heads if needed"]
  M --> N["Recompute eligibility for both families"]
  N --> O["Notify both families and write audit"]
```

---

### 2.4 Automated Scheme Eligibility & Application Tracking
The platform continuously evaluates family profiles against Gujarat State and Central Government welfare schemes.

#### Eligibility Assessment State Lifecycle
```mermaid
stateDiagram-v2
  [*] --> NOT_ASSESSED
  NOT_ASSESSED --> AUTO_ELIGIBLE: all rules pass
  NOT_ASSESSED --> AUTO_INELIGIBLE: a rule fails
  NOT_ASSESSED --> DOCS_NEEDED: document missing
  DOCS_NEEDED --> AUTO_ELIGIBLE: document verified and rules pass
  DOCS_NEEDED --> AUTO_INELIGIBLE: rules fail
  AUTO_ELIGIBLE --> OFFICER_CONFIRMED: officer confirms
  AUTO_ELIGIBLE --> OFFICER_REJECTED: officer rejects
  OFFICER_CONFIRMED --> NOT_ASSESSED: data or rule change
  OFFICER_REJECTED --> NOT_ASSESSED: new evidence
  AUTO_INELIGIBLE --> NOT_ASSESSED: data change
```

#### Application Tracking Lifecycle
```mermaid
stateDiagram-v2
  [*] --> NOT_APPLIED
  NOT_APPLIED --> APPLY_CLICKED: user opens official link
  APPLY_CLICKED --> APPLIED: source system reports submission
  NOT_APPLIED --> APPLIED: user links an existing reference
  APPLIED --> UNDER_REVIEW: source reports processing
  UNDER_REVIEW --> APPROVED: source approves
  UNDER_REVIEW --> REJECTED: source rejects
  APPROVED --> BENEFIT_RECEIVED: source reports disbursement
  REJECTED --> NOT_APPLIED: user may reapply
  BENEFIT_RECEIVED --> [*]
```

---

### 2.5 Aapnu Mitra AI Chatbot Widget
An interactive floating assistant widget (`AIChatbotWidget.tsx`) integrated across citizen and officer dashboards powered by `POST /api/v1/chatbot/query`:
- **High-Contrast Design**: Styled with a dark slate background (`bg-slate-900`) and high-visibility gold text (`text-amber-400`).
- **Real-Time Guidance**: Offers instant answers regarding state scheme criteria, document vault verifications, step-by-step lineage splits, and Family ID lookups.

---

## 📊 3. Entity-Relationship (ER) Diagram & Schema Overview

The underlying database ensures relational integrity between individuals, households, life events, scheme rules, and access audit trails.

```mermaid
erDiagram
  DISTRICT ||--o{ PINCODE_MASTER : contains
  PINCODE_MASTER ||--o{ ADDRESS : used_in
  ADDRESS ||--o{ FAMILY : located_at

  PERSON ||--o{ FAMILY_MEMBERSHIP : has
  FAMILY ||--o{ FAMILY_MEMBERSHIP : has
  PERSON ||--o| USER_ACCOUNT : may_have
  USER_ACCOUNT ||--o{ OFFICER_JURISDICTION : scoped_by
  USER_ACCOUNT ||--o{ OTP_CHALLENGE : requests

  PERSON ||--o{ DOCUMENT : owns
  FAMILY ||--o{ DOCUMENT : owns

  SCHEME_CATEGORY ||--o{ SCHEME : groups
  SCHEME ||--o{ ELIGIBILITY_ASSESSMENT : assessed_for
  FAMILY ||--o{ ELIGIBILITY_ASSESSMENT : subject_family
  PERSON ||--o{ ELIGIBILITY_ASSESSMENT : subject_person

  SCHEME ||--o{ APPLICATION : applied_under
  PERSON ||--o{ APPLICATION : applicant
  FAMILY ||--o{ APPLICATION : household
  APPLICATION ||--o{ APPLICATION_STATUS_HISTORY : tracks

  FAMILY ||--o{ FAMILY_EVENT : has
  FAMILY_EVENT ||--o{ FAMILY_LINEAGE : creates
  FAMILY ||--o{ FAMILY_VERSION : snapshots
  FAMILY ||--o{ ANOMALY_FLAG : flagged

  PERSON ||--o{ DUPLICATE_FLAG : person_a
  PERSON ||--o{ CONSENT_RECORD : gives
  PERSON ||--o{ CORRECTION_REQUEST : raises
  USER_ACCOUNT ||--o{ AUDIT_LOG : acts
  USER_ACCOUNT ||--o{ NOTIFICATION : receives

  DISTRICT {
    int district_code PK
    string name
  }
  PINCODE_MASTER {
    string pincode PK
    int district_code FK
    string taluka
    string area_name
  }
  ADDRESS {
    uuid address_id PK
    string line1
    string village_or_town
    string taluka
    int district_code FK
    string pincode FK
  }
  PERSON {
    uuid person_id PK
    string full_name
    date dob
    string gender
    string mobile
    string aadhaar_last4
    string aadhaar_hash UK
    string verification_status
    string social_category
    boolean is_deceased
  }
  FAMILY {
    string family_id PK
    string status
    uuid address_id FK
    string ration_card_type
    string income_band
    float land_holding_acres
    string registered_by
    datetime created_at
  }
  FAMILY_MEMBERSHIP {
    uuid membership_id PK
    uuid person_id FK
    string family_id FK
    string role_in_family
    string relation_to_head
    date start_date
    date end_date
    string start_reason
    string end_reason
  }
  USER_ACCOUNT {
    uuid user_id PK
    uuid person_id FK
    string role
    string login_id UK
    string password_hash
    string status
  }
  OFFICER_JURISDICTION {
    uuid id PK
    uuid user_id FK
    string scope_type
    int district_code
    string pincode
  }
  OTP_CHALLENGE {
    uuid challenge_id PK
    uuid user_id FK
    string purpose
    string code_hash
    datetime expires_at
    int attempts
  }
  DOCUMENT {
    uuid document_id PK
    uuid person_id FK
    string family_id FK
    string doc_type
    string status
    string file_ref
    date valid_until
  }
  SCHEME_CATEGORY {
    int category_id PK
    string name
  }
  SCHEME {
    uuid scheme_id PK
    string code UK
    string name
    string level
    string department
    int category_id FK
    string eligibility_unit
    string official_url
    string source_system
    datetime last_synced_at
  }
  ELIGIBILITY_ASSESSMENT {
    uuid assessment_id PK
    uuid scheme_id FK
    string subject_type
    string family_id FK
    uuid person_id FK
    string auto_result
    string review_status
    string rule_version
    datetime computed_at
  }
  APPLICATION {
    uuid application_id PK
    uuid scheme_id FK
    uuid person_id FK
    string family_id FK
    string external_ref
    string status
    datetime status_updated_at
  }
  APPLICATION_STATUS_HISTORY {
    uuid id PK
    uuid application_id FK
    string status
    datetime at
    string source
  }
  FAMILY_EVENT {
    uuid event_id PK
    string family_id FK
    string event_type
    string status
    date effective_date
    uuid requested_by
    uuid reviewed_by
  }
  FAMILY_LINEAGE {
    uuid id PK
    string parent_family_id FK
    string child_family_id FK
    uuid event_id FK
    string relation
  }
  FAMILY_VERSION {
    uuid id PK
    string family_id FK
    int version_no
    datetime valid_from
    datetime valid_to
  }
  DUPLICATE_FLAG {
    uuid flag_id PK
    uuid person_a FK
    uuid person_b FK
    float score
    string severity
    string status
  }
  ANOMALY_FLAG {
    uuid flag_id PK
    string family_id FK
    uuid event_id FK
    int score
    string status
  }
  CONSENT_RECORD {
    uuid consent_id PK
    uuid person_id FK
    string purpose
    datetime granted_at
    datetime revoked_at
  }
  CORRECTION_REQUEST {
    uuid request_id PK
    uuid person_id FK
    string target_entity
    string target_field
    string status
  }
  AUDIT_LOG {
    uuid log_id PK
    uuid actor_user_id FK
    string action
    string entity_type
    string entity_id
    string family_id
    datetime at
  }
  NOTIFICATION {
    uuid notification_id PK
    uuid user_id FK
    string channel
    string template
    string status
  }
```

### Entity Summary
| Entity | Purpose | Key Attributes |
|---|---|---|
| **`PERSON`** | Permanent individual identity across life | `person_id`, `aadhaar_hash`, `full_name`, `dob`, `gender` |
| **`FAMILY`** | Household container | `family_id` (12-digit Verhoeff), `status`, `pincode`, `district_code` |
| **`MEMBERSHIP`** | Dated link connecting Person to Family | `membership_id`, `person_id`, `family_id`, `role`, `is_active` |
| **`LIFE_EVENT`** | Audit trail of family changes | `event_id`, `event_type` (SPLIT/BIRTH/DEATH), `parent_family_id`, `child_family_id` |
| **`SCHEME`** | Catalog of state & central schemes | `scheme_id`, `scheme_name`, `category`, `eligibility_unit` |
| **`SCHEME_ASSESSMENT`** | Computed eligibility results | `assessment_id`, `family_id`, `status`, `reasons` |
| **`AUDIT_LOG`** | Consent & privacy tracking log | `log_id`, `family_id`, `accessor_role`, `action`, `timestamp` |

---

## 🔄 4. Detailed Data Flow & Sequence Diagrams

### 4.1 Citizen & Officer Screen Navigation Flow
```mermaid
flowchart LR
  H(["Family head"])
  M(["Family member"])
  FO(["Field officer"])
  DO(["District officer"])
  SA(["State admin"])
  SRC(["Source systems"])

  subgraph SYS["Aapnu Parivar"]
    U1("Register family")
    U2("Verify member via Aadhaar")
    U3("Manage family members")
    U4("Request life event")
    U5("Browse all schemes")
    U6("View my eligible schemes")
    U7("Apply on official site")
    U8("Track applications")
    U9("View consent and access log")
    U10("Request data correction")
    U11("Register family on behalf")
    U12("Verify family record")
    U13("Confirm eligibility")
    U14("Review duplicate flags")
    U15("Approve life events")
    U16("View district or pincode dashboard")
    U17("View statewide analytics")
    U18("Sync schemes and statuses")
  end

  H --- U1
  H --- U3
  H --- U4
  H --- U10
  M --- U2
  M --- U5
  M --- U6
  M --- U7
  M --- U8
  M --- U9
  H --- U5
  H --- U6
  H --- U7
  H --- U8
  H --- U9
  FO --- U11
  FO --- U12
  DO --- U12
  DO --- U13
  DO --- U14
  DO --- U15
  DO --- U16
  SA --- U17
  SA --- U16
  SRC --- U18
```

### 4.2 Login Navigation Flow
```mermaid
flowchart TD
  A["Open app"] --> B["Enter mobile number or Family ID"]
  B --> C{"Login method"}
  C -- Password --> D["Enter password"]
  C -- OTP --> E["Request OTP (shown in demo banner)"]
  C -- Forgot password --> F["Request OTP"]
  D --> G{"Valid?"}
  E --> H["Enter OTP"]
  F --> I["Enter OTP and set new password"]
  H --> G
  I --> G
  G -- No --> J["Show error and count attempt"]
  J --> K{"Too many attempts?"}
  K -- Yes --> L["Temporary lockout"]
  K -- No --> C
  G -- Yes --> M["Resolve role from active membership"]
  M --> N["Issue access and refresh tokens"]
  N --> O["Family dashboard"]
```

### 4.3 Family Registration Sequence Flow
```mermaid
flowchart TD
  A["Entry screen: Register a new family"] --> B["Create account: mobile number and OTP"]
  B --> C["Step 1: head details"]
  C --> D["Step 2: add members and relations"]
  D --> E["Step 3: Aadhaar verification for each adult (mock OTP)"]
  E --> F{"Duplicate check"}
  F -- "Exact match" --> G["Block: person already in a family. Explain leave-family or join-request"]
  F -- "Possible match" --> H["Continue and open duplicate flag"]
  F -- "Clear" --> I["Step 4: address, ration card, income, land, housing"]
  H --> I
  I --> J["Step 5: consent"]
  J --> K["Step 6: review and submit"]
  K --> L["Family ID issued, status SUBMITTED"]
  L --> M["Eligibility runs automatically for verified members"]
  L --> N["Officer verification queue"]
  N --> O{"Officer decision"}
  O -- Verify --> P["Status VERIFIED"]
  O -- Send back --> Q["Status NEEDS_CORRECTION"]
```

### 4.4 Member Aadhaar Verification Sequence
```mermaid
sequenceDiagram
  autonumber
  actor C as Citizen
  participant FE as React app
  participant API as FastAPI
  participant V as Verification service
  participant D as Duplicate service
  participant DB as Database
  participant E as Eligibility engine
  C->>FE: Fill registration steps
  FE->>API: POST /families (draft with members)
  API->>D: Check duplicates for each person
  D->>DB: Query candidates by hash, DOB, mobile, pincode
  D-->>API: Clear, flagged or blocked
  FE->>API: POST /members/{id}/verify/start (Aadhaar number)
  API->>V: Request e-KYC OTP (mock UIDAI)
  V-->>API: OTP sent
  FE->>API: POST /members/{id}/verify/confirm (OTP)
  API->>V: Confirm OTP
  V-->>API: Verified with name, DOB, gender
  API->>DB: Store last four digits and keyed hash, mark VERIFIED
  FE->>API: POST /families/{id}/submit
  API->>DB: Issue Family ID, write memberships, consents, audit
  API->>E: Run eligibility for verified members
  E->>DB: Store assessments
  API-->>FE: Family ID and status SUBMITTED
```

### 4.5 Citizen Scheme Discovery & Apply Flow
```mermaid
flowchart TD
  A["Login"] --> B["Family dashboard"]
  B --> C["Open My schemes"]
  C --> D["Choose scope: whole family or a member"]
  D --> E["See three groups: Eligible, Documents needed, Not eligible"]
  E --> F["Open a scheme card"]
  F --> G["See badge Central or Gujarat, benefit, why eligible, confirmation state"]
  G --> H{"Member verified?"}
  H -- No --> I["Prompt: verify with Aadhaar to apply"]
  H -- Yes --> J{"Apply allowed by scheme setting?"}
  J -- "Waiting for officer confirmation" --> K["Apply disabled with explanation"]
  J -- Yes --> L["Apply on official site opens in new tab"]
  L --> M["Click logged, status APPLY_CLICKED"]
  M --> N["Return later or link reference number"]
  N --> O["Connector sync updates status"]
  O --> P["Application tracker and notification"]
```

### 4.6 Eligibility Verification Sequence
```mermaid
sequenceDiagram
  autonumber
  actor C as Citizen
  participant FE as React app
  participant API as FastAPI
  participant S as Scheme and application service
  participant K as Connector
  participant SRC as Source system (mock)
  C->>FE: Click Apply on official site
  FE->>API: POST /applications/apply-click (scheme, member)
  API->>S: Check verified member and apply rules
  S-->>API: Allowed and official URL
  API-->>FE: Official URL
  FE->>SRC: Open official site in new tab
  Note over C,SRC: Application is submitted on the official portal
  K->>SRC: Scheduled pull of application status
  SRC-->>K: Status for applicant token
  K->>S: Upsert application and status history
  S->>API: Notify family of status change
  C->>FE: Open tracker
  FE->>API: GET /applications
  API-->>FE: Statuses with last synced time
```

### 4.7 Household Split Sequence
```mermaid
sequenceDiagram
  autonumber
  actor M as Adult member
  participant FE as React app
  participant API as FastAPI
  participant EV as Life event service
  participant AN as Anomaly scorer
  participant DB as Database
  actor O as District officer
  M->>FE: Start split wizard
  FE->>API: POST /events/split (members, new address, evidence)
  API->>EV: Validate members and pending events
  EV->>AN: Compute anomaly score
  AN-->>EV: Score and signals
  alt Score below 50
    EV->>DB: Create new family and new Family ID
    EV->>DB: End old memberships and start new ones on same date
    EV->>DB: Write lineage, family versions, audit
    EV->>API: Recompute eligibility for both families
  else Score 50 or above
    EV->>DB: Store event as UNDER_REVIEW with anomaly flag
    O->>API: Review event in queue
    API->>EV: Approve or reject
  end
  API-->>FE: New Family ID or review status
```

### 4.8 Officer Jurisdiction Dashboard Workflow
```mermaid
flowchart TD
  A["Officer login"] --> B["Dashboard shows open duplicates in jurisdiction"]
  B --> C["Open duplicate queue"]
  C --> D["Select a flag"]
  D --> E["Side-by-side view: two persons, their families, addresses, documents, score and reasons"]
  E --> F{"Decision"}
  F -- "Not duplicate" --> G["Flag closed, persons unchanged"]
  F -- "Duplicate" --> H["Merge person records, keep history of both"]
  F -- "Needs info" --> I["Send correction request to family"]
  H --> J["Recompute eligibility and enrollments"]
  G --> K["Audit entry written"]
  I --> K
  J --> K
```

### 4.9 Privacy & Consent Audit Flow
```mermaid
flowchart TD
  A["Login"] --> B["Open Privacy"]
  B --> C["Tab 1: Consents given, purpose, date, mandatory or optional"]
  B --> D["Tab 2: Access log"]
  D --> E["Filter by date, role, purpose"]
  E --> F["Each row: who accessed, which record, why, when"]
  C --> G{"Optional consent?"}
  G -- Yes --> H["Revoke consent"]
  H --> I["Effect explained and audit entry written"]
  G -- No --> J["Explain why it is required"]
```

### 4.10 Comprehensive System Data Flow
```mermaid
flowchart LR
  CIT["Citizen (head or member)"]
  OFF["Government officer"]
  UID["Aadhaar e-KYC (mock)"]
  SRC["Scheme source systems (mock)"]
  RAT["Ration card and document locker (mock)"]
  MSG["SMS / WhatsApp gateway (future)"]

  P0(("0. Aapnu Parivar"))

  CIT -->|"registration data, verification OTP, event requests, apply clicks"| P0
  P0 -->|"Family ID, eligible schemes, application status, notifications"| CIT
  OFF -->|"family registration, verification, confirmations, decisions"| P0
  P0 -->|"queues, dashboards, flags, audit log"| OFF
  P0 -->|"e-KYC request"| UID
  UID -->|"verification result"| P0
  P0 -->|"scheme and status requests with applicant token"| SRC
  SRC -->|"scheme master data, application status"| P0
  P0 -->|"document and card lookups"| RAT
  RAT -->|"document verification"| P0
  P0 -.->|"messages"| MSG
```

### 4.11 Aadhaar Verification & e-KYC Flow
```mermaid
flowchart LR
  CIT["Citizen"]
  OFF["Officer"]
  UID["Aadhaar e-KYC (mock)"]
  SRC["Source systems (mock)"]
  DOC["Document locker (mock)"]

  P1("1.0 Authenticate and manage accounts")
  P2("2.0 Register and manage family")
  P3("3.0 Verify identity and detect duplicates")
  P4("4.0 Process life events")
  P5("5.0 Assess eligibility")
  P6("6.0 Sync schemes and application status")
  P7("7.0 Review and confirm")
  P8("8.0 Analytics and dashboards")
  P9("9.0 Audit, consent and notify")

  D1[("D1 Persons, families, memberships")]
  D2[("D2 Events, lineage, versions")]
  D3[("D3 Schemes and rules")]
  D4[("D4 Assessments and applications")]
  D5[("D5 Audit, consent, notifications")]

  CIT -->|"credentials, OTP"| P1
  P1 -->|"tokens, role"| CIT
  CIT -->|"family and member data"| P2
  OFF -->|"on-behalf registration"| P2
  P2 <--> D1
  P2 -->|"persons to check"| P3
  P3 -->|"e-KYC request"| UID
  UID -->|"result"| P3
  P3 <--> D1
  P3 -->|"duplicate flags"| P7
  CIT -->|"event request"| P4
  P4 <--> D1
  P4 --> D2
  P4 -->|"changed families"| P5
  P4 -->|"anomaly flags"| P7
  P2 -->|"new or changed profile"| P5
  DOC -->|"verified documents"| P5
  P5 -->|"read persons, families"| D1
  P5 -->|"read rules"| D3
  P5 -->|"write assessments"| D4
  P5 -->|"auto results"| P7
  SRC -->|"schemes"| P6
  SRC -->|"application status"| P6
  P6 --> D3
  P6 --> D4
  P6 -->|"status changes"| P9
  OFF -->|"decisions"| P7
  P7 --> D4
  P7 --> D1
  P7 --> D2
  P7 -->|"outcomes"| P9
  D1 --> P8
  D4 --> P8
  D2 --> P8
  P8 -->|"dashboards"| OFF
  P8 -->|"family summary, my schemes"| CIT
  P1 --> D5
  P2 --> D5
  P7 --> D5
  P9 --> D5
  P9 -->|"notifications, access log"| CIT
```

### 4.12 Automated Eligibility Engine Pipeline
```mermaid
flowchart TD
  T["Trigger: profile change, document change, life event, rule version change"] --> A["5.1 Select affected families and persons"]
  A --> B["5.2 Load facts: person fields, family fields, verified documents"]
  B --> C["5.3 Load active schemes and rule files"]
  C --> D["5.4 Evaluate each rule per scheme and subject"]
  D --> E{"All rules satisfied?"}
  E -- Yes --> F["Result AUTO_ELIGIBLE"]
  E -- "No, a document is missing" --> G["Result DOCS_NEEDED with list"]
  E -- "No, a rule fails" --> H["Result AUTO_INELIGIBLE with reasons"]
  F --> I["5.5 Store assessment, mark old one not current"]
  G --> I
  H --> I
  I --> J["5.6 Queue AUTO_ELIGIBLE for officer confirmation"]
  I --> K["5.7 Notify family of changes"]
  J --> L["Officer queue"]
```

---

## 🔮 5. Future Architecture & Technical Roadmap

### 5.1 Strategic Roadmap Phases
| Phase | Milestone Focus | Deliverables |
|---|---|---|
| **Phase 1** | MVP Core Platform | English Web UI, Synthetic Data Generator, Verhoeff IDs, Split Engine, Officer Dashboard |
| **Phase 2** | Regional & Mobile Expansion | **Gujarati Localization (`gu`)**, SMS/WhatsApp OTP delivery, Field Officer PWA Offline Mode |
| **Phase 3** | National Integrations | Live Aadhaar e-KYC Vault, DigiLocker, Ration Card DB, State Direct Benefit Transfer (DBT) |
| **Phase 4** | Advanced AI & Analytics | Voice-enabled Gujarati AI Assistant, Machine Learning Anomaly Detection for splits |
| **Phase 5** | Statewide Scalability | Microservice Architecture, API Gateway, Distributed Message Queue, Multi-zone DB |

### 5.2 Enterprise Distributed Microservices Architecture
```mermaid
flowchart TB
  subgraph EDGE["Edge"]
    WEB["Web and PWA (Gujarati and English)"]
    MOB["Mobile app"]
    KIOSK["Field officer offline app"]
  end

  GW["API gateway: authentication, rate limits, routing"]

  subgraph SVC["Services"]
    IDS["Identity and family service"]
    EVS["Life event service"]
    ELS["Eligibility service"]
    CNS["Connector service"]
    NTS["Notification service"]
    CMS["Consent manager"]
    ANS["Analytics service"]
    AIS["AI service: chatbot, anomaly, matching"]
  end

  BUS[["Message queue / event stream"]]

  subgraph DATA["Data"]
    PG[("PostgreSQL, partitioned by district")]
    SRCH[("Search index")]
    CACHE[("Cache")]
    VAULT[("Aadhaar data vault")]
    WH[("Analytics warehouse")]
    OBJ[("Encrypted document store")]
  end

  subgraph EXT["External systems"]
    AUTH["Aadhaar authentication"]
    RAT["Ration card and NFSA"]
    DLK["Document locker"]
    PORT["Scheme portals and DBT"]
    MSG["SMS and WhatsApp providers"]
  end

  WEB --> GW
  MOB --> GW
  KIOSK --> GW
  GW --> IDS
  GW --> EVS
  GW --> ELS
  GW --> ANS
  GW --> AIS
  IDS --> BUS
  EVS --> BUS
  BUS --> ELS
  BUS --> NTS
  BUS --> ANS
  ELS --> CNS
  IDS --> CMS
  CNS --> AUTH
  CNS --> RAT
  CNS --> DLK
  CNS --> PORT
  NTS --> MSG
  IDS --> PG
  EVS --> PG
  ELS --> PG
  IDS --> VAULT
  IDS --> SRCH
  IDS --> CACHE
  ANS --> WH
  IDS --> OBJ
```

---

## 🛠️ 6. Quick Start & Local Development

### Prerequisites
- **Python 3.10+**
- **Node.js 18+ & npm**

### 1. Backend Setup (FastAPI)
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt

# Seed synthetic Gujarat households
python -m app.seed.synthetic_generator

# Start API server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:5173`** in your browser.

### 3. Run Automated Tests
```bash
cd backend
pytest
```

---

## 🔑 7. Default Demo Credentials

Use these pre-seeded credentials to explore and test the platform:

### 🏛️ Government Official & Admin Logins
*(Routes automatically to the **Departmental Officer Console** at `/officer`)*

| Role | Login Identifier | Default Password | Jurisdiction Scope |
|---|---|---|---|
| **State Admin** | `admin@gujarat.gov.in` | `Admin@123` | Statewide (All Gujarat Districts) |
| **District Officer** | `district07@gujarat.gov.in` | `District@123` | District 07 (Bhavnagar) |
| **Field Officer** | `field0701@gujarat.gov.in` | `Field@123` | Pincode 364001 |

### 🏡 Citizen & Family Portal Login
*(Routes automatically to the **Citizen Family Portal** at `/my-family`)*

| Role | Login Identifier | Default Password | Access Features |
|---|---|---|---|
| **Family Head** | `9876543210` | `Citizen@123` | Household Entitlements, Verhoeff Family ID, Member Roster, 4-Step Household Split Wizard, Document Vault, and **Aapnu Mitra AI Chatbot** |

### 💡 Google OAuth (Gmail) Login Simulation
- Signing in via the **Google Sign-In** tab using an official email ending in `@gujarat.gov.in` (e.g. `admin@gujarat.gov.in`) automatically grants **Officer Dashboard** access.
- Signing in using any standard Gmail address (e.g. `citizen@gmail.com`) automatically routes to the **Citizen Family Portal**.

---

*Aapnu Parivar — One Family. One ID. Every Benefit.*
