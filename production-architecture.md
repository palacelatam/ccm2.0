# CCM 2.0 Production Architecture Document

## Document Version
**Version:** 1.0
**Date:** October 13, 2025
**Purpose:** Comprehensive production architecture blueprint for Client Confirmation Manager 2.0

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [System Overview](#2-system-overview)
3. [Google Cloud Platform Foundation](#3-google-cloud-platform-foundation)
4. [Application Architecture](#4-application-architecture)
5. [Data Architecture](#5-data-architecture)
6. [Security Architecture](#6-security-architecture)
7. [Integration Architecture](#7-integration-architecture)
8. [Deployment Architecture](#8-deployment-architecture)
9. [Networking & Connectivity](#9-networking--connectivity)
10. [Monitoring & Observability](#10-monitoring--observability)
11. [Disaster Recovery & Business Continuity](#11-disaster-recovery--business-continuity)
12. [Scalability & Performance](#12-scalability--performance)
13. [Cost Optimization](#13-cost-optimization)
14. [Migration Path](#14-migration-path)

---

## 1. Executive Summary

### 1.1 Purpose
The Client Confirmation Manager (CCM) 2.0 is a multi-tenant SaaS platform designed to streamline foreign exchange trade confirmations for banking clients in Chile and Latin America. The system automatically processes email confirmations from multiple banks, extracts trade data using AI, matches against client records, and generates automated responses.

### 1.2 Key Business Capabilities
- **Automated Email Processing**: Monitors and processes trade confirmation emails from multiple banks
- **AI-Powered Data Extraction**: Uses Vertex AI for intelligent PDF and email parsing
- **Multi-Bank Integration**: Handles different confirmation formats from various financial institutions
- **Real-time Matching**: Automatic matching of email confirmations with client trade records
- **Automated Response Generation**: Sends confirmation or dispute emails based on matching results
- **Multi-Language Support**: Full support for Spanish, English, and Portuguese
- **Settlement Template Management**: Internal administration of bank settlement instruction templates

### 1.3 Technical Highlights
- **Cloud-Native Architecture**: Built entirely on Google Cloud Platform
- **Microservices Design**: Modular, scalable backend services
- **CMEK Encryption**: Customer-managed encryption keys for all data at rest
- **Multi-Tenant SaaS**: Single pooled infrastructure with application-level isolation
- **Enterprise Security Foundation**: Google Cloud Foundation with ISO 27001-ready controls
- **Zero-Trust Security**: Multiple layers of authentication and authorization

---

## 2. System Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        External Systems                          │
├─────────────────────────────────────────────────────────────────┤
│ • Bank Email Servers (SMTP/IMAP)                                │
│ • Client Email Systems                                          │
│ • Client File Sources (SFTP/Cloud Storage)                     │
│ • Bank Trading Systems (Future API Integration)                 │
│ • SMS Gateway (MessageBird)                                     │
│ • Banco Central API (Exchange Rates)                            │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Edge & Security Layer                           │
├─────────────────────────────────────────────────────────────────┤
│ • Global Load Balancer (api.servicios.palace.cl)                │
│ • Cloud Armor (DDoS + IP Whitelisting - attached to LB)         │
│ • Firebase Hosting (app.servicios.palace.cl)                    │
│ • SSL/TLS Termination (both domains)                            │
│ • WAF Rules                                                     │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Application Layer                              │
├─────────────────────────────────────────────────────────────────┤
│ Frontend (Firebase Hosting)          Backend (Cloud Run)        │
│ • React SPA                          • FastAPI Services         │
│ • AG-Grid Enterprise                 • JWT Authentication       │
│ • Material-UI Components             • Trade Processing API     │
│ • i18next Localization              • Email Processing API     │
│ • Firebase Auth + 2FA               • File Sync Service        │
│                                      • Admin API                │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Data Layer                                │
├─────────────────────────────────────────────────────────────────┤
│ Firestore (CMEK)           Cloud Storage (CMEK)   Cloud Tasks   │
│ • Client Data              • PDF Attachments      • Email Queue │
│ • Trade Records            • CSV/Excel Uploads    • SMS Queue   │
│ • Email Confirmations      • Synced Trade Files   • File Sync   │
│ • User Profiles            • Templates            • Processing  │
│ • Sync Configurations      • Audit Logs                         │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Processing & Integration Layer                │
├─────────────────────────────────────────────────────────────────┤
│ • Gmail API + Pub/Sub (Email Push Notifications)                │
│ • Vertex AI (Claude Sonnet 4.5 / Gemini 2.5 Pro)               │
│ • Cloud Scheduler (Warm-up + File Sync Triggers)                │
│ • Cloud KMS (Customer-Managed Encryption Keys)                  │
│ • Secret Manager (Credentials + API Keys)                       │
│ • Cloud Tasks (Async Processing Queues)                         │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Deployment Architecture

#### 2.2.1 Multi-Tenant SaaS Model
- **Target Clients**: Companies that trade FX with banks (from SMEs to large corporations)
- **Architecture**: Single pooled infrastructure serving all clients
- **Data Isolation**: Application-level separation using organizationId
- **Cost Model**: Subscription-based SaaS pricing
- **Compliance**: ISO 27001 primary, SOC 2 Type 2 secondary

#### 2.2.2 Bank Integration Model

**Initial Setup**:
- Banks do not have direct access to the platform
- Palace administrators manage bank templates internally
- Bank admin accounts exist for internal use only

**For Future Development**:
- Bank portal for direct template management
- Bank user authentication and dashboards
- Self-service settlement instruction uploads

---

## 3. Google Cloud Platform Foundation

### 3.1 Organization Structure

**Current Setup**: Google Cloud Foundation best practices architecture
- Built using Google's enterprise blueprint for security and scalability
- Provides environment isolation, centralized networking, and unified security
- Designed for growth while maintaining security standards

```
palace.cl (Organization ID: 165254678508)
├── Production/
│   ├── prod1-svc-5q4z* (Primary production - auto-generated name)
│   ├── prod2-svc-5q4z* (Secondary production - auto-generated name)
│   └── kms-proj-[id] (Encryption keys for prod)
├── Non-Production/
│   ├── nonprod1-svc-5q4z* (Staging/QA - auto-generated name)
│   ├── nonprod2-svc-5q4z* (Testing - auto-generated name)
│   └── kms-proj-[id] (Encryption keys for non-prod)
├── Development/
│   ├── ccm-dev-pool (Active development - manually named)
│   └── kms-proj-[id] (Encryption keys for dev)
└── Common/
    ├── vpc-host-prod-oj681-ps264* (Production networking)
    ├── vpc-host-nonprod-pf819-wa214* (Non-prod networking)
    └── central-log-monitor-rp135-mx78* (Centralized logging)

* Auto-generated names from Google Cloud Foundation setup - kept as-is
```

**Note on Project Names**:
The seemingly random project names (like `prod1-svc-5q4z`) were auto-generated by Google Cloud Foundation setup. While not intuitive, we're keeping them to avoid migration complexity. The structure itself follows best practices.

**Why This Structure**:
- **Environment Isolation**: Complete separation between Dev/Test/Prod (critical for ISO 27001)
- **Shared VPC**: Centralized network management and security controls
- **Centralized Logging**: Single location for all audit trails and monitoring
- **CMEK per Environment**: Separate encryption keys for each environment

### 3.2 Network Architecture

#### 3.2.1 Multi-Region Strategy (Required)

**Why Multi-Region is Necessary**:
- **southamerica-west1** (Santiago): Primary data location for Chilean clients
  - Firestore, Cloud Storage, KMS available ✅
  - Cloud Tasks NOT available ❌
  - Vertex AI NOT available ❌

- **us-east4** (N. Virginia): Required for services
  - Cloud Tasks (async processing) ✅
  - Vertex AI (LLM processing) ✅
  - Minimal data, just service endpoints

**Cost-Optimized Multi-Region Design**:
```
southamerica-west1: Core application and data (minimize egress)
us-east4: Service APIs only (Cloud Tasks, Vertex AI)
Cross-region traffic: ~$0.02/GB (minimal - only API calls)
```

#### 3.2.2 Network Configuration
**Production VPC**: `vpc-host-prod-oj681-ps264`
- Santiago subnet: `10.1.1.0/24`
- Virginia subnet: `10.1.2.0/24`
- VPC Flow Logs enabled for security monitoring
- Private Google Access for secure service connectivity

#### 3.2.3 Load Balancer & Cloud Armor Configuration

**Architecture Requirements**:
- **Global Load Balancer**: Required for Cloud Armor ($25/month)
- **Backend Service**: Points to Cloud Run in southamerica-west1
- **Cloud Armor Policy**: Attached to Load Balancer backend

**IP Whitelisting Implementation**:
```yaml
Cloud Armor Security Policy:
  Default Rule: Deny all (403 Forbidden)
  Client Rules:
    - Priority 100: Allow Client-A office IPs (200.28.1.0/24)
    - Priority 101: Allow Client-A VPN (200.28.2.5/32)
    - Priority 200: Allow Client-B network (190.45.3.0/24)
    - Priority 999: Allow Palace office (for admin access)
```

**Benefits of Load Balancer Approach**:
- Blocks malicious traffic at edge (never reaches backend)
- DDoS protection included automatically
- Centralized security logging and monitoring
- ISO 27001 compliant architecture
- Professional enterprise-grade security

### 3.3 Security Policies (Explained)

#### Organization-Wide Policies and Their Purpose

**No Service Account Keys** (`constraints/iam.disableServiceAccountKeyCreation`)
- **What**: Prevents downloading JSON key files
- **Why**: Keys can be accidentally exposed in code/Git
- **Impact**: Forces use of safer authentication methods
- **Exception**: Gmail API requires key (controlled exception exists)

**Mandatory Encryption** (`constraints/gcp.restrictNonCmekServices`)
- **What**: All data must use YOUR encryption keys, not Google's
- **Why**: ISO 27001 requirement - you control data encryption
- **Impact**: Small cost (~$0.06/month per key) but major security benefit

**No Public Storage** (`constraints/storage.publicAccessPrevention`)
- **What**: Prevents making Cloud Storage buckets publicly accessible
- **Why**: #1 cause of data breaches is misconfigured storage
- **Impact**: None - you don't need public buckets

**Secure Boot VMs** (`constraints/compute.requireShieldedVm`)
- **What**: VMs must have verified boot and integrity monitoring
- **Why**: Prevents rootkits and boot-level malware
- **Impact**: Automatic with Cloud Run - no action needed

---

## 4. Application Architecture

### 4.1 Frontend Architecture

#### 4.1.1 Technology Stack
- **Framework**: React 18.x with TypeScript
- **UI Library**: Material-UI v5
- **Data Grid**: AG-Grid Enterprise (licensed)
- **State Management**: React Context API
- **Routing**: React Router v6
- **Internationalization**: i18next
- **Build Tool**: Create React App (ejected)

#### 4.1.2 Key Features
- **Single Page Application** with lazy loading
- **Progressive Web App** capabilities
- **Responsive Design** for mobile/tablet/desktop
- **Dark Mode** support throughout
- **Offline Capability** with service workers

#### 4.1.3 Deployment
- **Hosting**: Firebase Hosting with CDN
- **Domain**: `app.palace.cl` (production)
- **SSL**: Automated via Firebase
- **Cache Strategy**: Aggressive caching for static assets

### 4.2 Backend Architecture

#### 4.2.1 Technology Stack
- **Framework**: FastAPI (Python 3.11)
- **Data Validation**: Pydantic v2
- **Database Client**: Firebase Admin SDK
- **Task Queue**: Google Cloud Tasks
- **Authentication**: Firebase Auth + Custom JWT
- **Container Runtime**: Docker on Cloud Run

#### 4.2.2 Service Architecture

```python
backend/src/
├── api/                    # REST API Endpoints
│   ├── v1/
│   │   ├── auth/          # Authentication endpoints
│   │   ├── clients/       # Client management
│   │   ├── trades/        # Trade processing
│   │   ├── emails/        # Email operations
│   │   ├── admin/         # Admin functions
│   │   └── reports/       # Reporting endpoints
├── services/              # Business Logic
│   ├── auth_service.py    # Authentication/Authorization
│   ├── client_service.py  # Client operations
│   ├── trade_service.py   # Trade matching logic
│   ├── email_service.py   # Email processing
│   ├── gmail_service.py   # Gmail API integration
│   ├── llm_service.py     # AI/LLM operations
│   ├── sms_service.py     # SMS notifications
│   └── task_service.py    # Cloud Tasks management
├── models/                # Data Models
│   ├── user.py
│   ├── client.py
│   ├── trade.py
│   ├── email.py
│   └── settlement.py
├── agents/                # Autonomous Agents
│   ├── email_parser.py    # Email parsing agent
│   ├── trade_matcher.py   # Trade matching agent
│   └── report_generator.py # Report generation agent
└── utils/                 # Utilities
    ├── validators.py
    ├── transformers.py
    └── constants.py
```

#### 4.2.3 API Design Principles
- **RESTful**: Standard HTTP methods and status codes
- **Versioned**: `/api/v1/` prefix for all endpoints
- **Authenticated**: JWT tokens for all protected endpoints
- **Rate Limited**: Per-client rate limiting
- **Documented**: Auto-generated OpenAPI/Swagger docs

### 4.3 Microservices Communication

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   API        │────▶│   Services   │
│   (React)    │◀────│   Gateway    │◀────│   (FastAPI)  │
└──────────────┘     └──────────────┘     └──────────────┘
                            │                      │
                            ▼                      ▼
                     ┌──────────────┐     ┌──────────────┐
                     │   Firebase   │     │  Cloud Tasks │
                     │     Auth     │     │    Queue     │
                     └──────────────┘     └──────────────┘
```

---

## 5. Data Architecture

### 5.1 Database Design (Firestore)

#### 5.1.1 Core Collections

```typescript
// Multi-tenant data structure
/roles/{roleId}
  - name: string
  - permissions: string[]
  - type: 'client_admin' | 'client_user' | 'bank_admin'

/users/{userId}
  - email: string
  - firstName: string
  - lastName: string
  - organizationId: string
  - organizationType: 'client' | 'bank'
  - roles: string[]
  - status: 'active' | 'inactive'
  - preferences: {
      language: 'es' | 'en' | 'pt'
      theme: 'light' | 'dark'
    }

/clients/{clientId}
  - name: string
  - taxId: string
  - status: 'active' | 'inactive'

  /settings/configuration
    - automationSettings: {
        autoConfirmMatched: boolean
        matchedDelayMinutes: number
        autoConfirmDisputed: boolean
        disputedDelayMinutes: number
      }
    - emailSettings: {
        defaultLanguage: string
        ccEmails: string[]
      }

  /bankAccounts/{accountId}
    - bankId: string
    - accountNumber: string
    - currency: string
    - isActive: boolean

  /trades/{tradeId}
    - tradeNumber: string
    - tradeDate: timestamp
    - settlementDate: timestamp
    - currency1: string
    - currency2: string
    - amount1: number
    - amount2: number
    - rate: number
    - direction: 'buy' | 'sell'
    - status: 'unmatched' | 'matched' | 'confirmed' | 'disputed'
    - bankId: string
    - uploadSessionId: string

  /emails/{emailId}
    - sender: string
    - subject: string
    - receivedDate: timestamp
    - attachments: string[]
    - llmExtractedData: {
        tradeNumber: string
        amount: number
        currency: string
        // ... other extracted fields
      }
    - status: 'unprocessed' | 'processed' | 'matched'

  /matches/{matchId}
    - tradeId: string
    - emailId: string
    - confidenceScore: number
    - matchedFields: string[]
    - differingFields: {
        fieldName: string
        clientValue: any
        emailValue: any
      }[]
    - status: 'pending' | 'confirmed' | 'disputed'
    - autoEmailSent: boolean
    - emailSentAt: timestamp

/banks/{bankId}
  - name: string
  - code: string
  - status: 'active' | 'inactive'

  /clientSegments/{segmentId}
    - name: string
    - criteria: object

  /settlementInstructionLetters/{letterId}
    - templateName: string
    - templatePath: string
    - variables: string[]
```

#### 5.1.2 Data Retention Policies
- **Trade Data**: 3 years (client business requirement)
- **Email Confirmations**: 3 years (same as trade data)
- **Audit Logs**: 3 years (ISO 27001 compliance)
- **User Activity Logs**: 1 year
- **Temporary Upload Data**: 30 days (auto-deleted after processing)

### 5.2 Cloud Storage Architecture

```
gs://ccm-prod-storage/
├── attachments/
│   ├── {clientId}/
│   │   ├── emails/
│   │   │   └── {emailId}/
│   │   │       └── {attachment_files}
│   │   └── uploads/
│   │       └── {sessionId}/
│   │           └── {uploaded_files}
├── templates/
│   ├── settlement-instructions/
│   │   └── {bankId}/
│   │       └── {template_files}
│   └── email-templates/
│       └── {language}/
│           └── {template_files}
├── exports/
│   └── {clientId}/
│       └── {export_date}/
│           └── {export_files}
└── backups/
    └── {backup_date}/
        └── {backup_files}
```

### 5.3 Data Encryption

#### 5.3.1 Understanding CMEK (Customer-Managed Encryption Keys)

**What is CMEK?**
- YOU own and control the encryption keys (not Google)
- Data is encrypted with YOUR keys stored in Cloud KMS
- Even Google cannot decrypt your data without your permission
- Keys automatically rotate every 90 days for security

**Why CMEK Matters**:
- **ISO 27001 Compliance**: Demonstrates data control
- **Client Confidence**: Banks/clients know you control encryption
- **Data Sovereignty**: You can revoke access by disabling keys
- **Cost**: Minimal (~$0.06/month per key)

**How CMEK Works**:
```
1. Data save requested → Firestore
2. Firestore → "Encrypt with customer key" → Cloud KMS
3. Cloud KMS encrypts data with your key
4. Encrypted data saved to disk
5. For reading: reverse process with same key
```

#### 5.3.2 CMEK Configuration
- **KMS Locations**:
  - southamerica-west1 (for Chilean data residency)
  - us-east4 (for services that require it)
- **Key Hierarchy**:
  ```
  Environment (Dev/Prod) Root Key
  ├── Firestore Database Encryption
  ├── Cloud Storage Bucket Encryption
  └── Secret Manager Encryption
  ```
- **Access Control**: Only specific service accounts can use keys
- **Audit Trail**: All key usage logged in Cloud Audit Logs

---

## 6. Security Architecture

### 6.1 Authentication & Authorization

#### 6.1.1 Firebase Authentication with 2FA

**Authentication Stack**:
- **Primary**: Firebase Authentication (managed service)
- **2FA Methods**:
  - TOTP (Time-based One-Time Password) - Google Authenticator, Authy
- **Session Management**: JWT tokens with 1-hour expiry
- **Refresh Strategy**: Silent token refresh before expiry

**Why Firebase + 2FA (Not SSO Yet)**:
- **Sufficient Security**: 2FA provides enterprise-grade protection
- **Lower Complexity**: No SAML/OIDC integration needed
- **Faster Time-to-Market**: Works out of the box
- **Future-Ready**: JWT architecture allows easy SSO addition later

**Authentication Flow**:
```
1. User enters email/password → Firebase Auth
2. Firebase validates credentials → Requests 2FA
3. User enters TOTP/SMS code → Firebase validates
4. Firebase generates JWT with custom claims:
   {
     "organizationId": "client_123",
     "organizationType": "client",
     "roles": ["client_admin"],
     "email": "user@company.com",
     "exp": 1234567890
   }
5. Frontend stores JWT → Sends with every API request
6. Backend validates JWT → Grants access
```

#### 6.1.2 Authorization Model (RBAC)

**Role Definitions**:
- **Client Admin**:
  - Full access to trade and administration data for their client
  - Can configure automation settings and user management
  - Full application user for trade monitoring and confirmation

- **Client User**:
  - Access to trade and confirmation data only
  - Cannot modify administrative settings
  - Full application user for trade monitoring and confirmation

- **Bank Admin** (Internal Use - Initial Phase):
  - Used by Palace staff to manage settlement instruction templates
  - No client data access
  - Banks don't login directly (future enhancement)

**Organization-Based Isolation**:
- Every query filtered by organizationId
- Users can only see their organization's data
- Enforced at both database and API levels

### 6.2 API Security

#### 6.2.1 Security Layers
1. **Cloud Armor + Load Balancer**:
   - DDoS protection and IP allowlisting at network edge
   - Requires Global Load Balancer (see Section 3.2.3)
   - Blocks unauthorized IPs before reaching backend

2. **Rate Limiting & Quota Management**:
   - **What it is**: Prevents API abuse and ensures fair usage
   - **Rate Limiting**: Max requests per minute (e.g., 100/min per user)
   - **Quota**: Monthly API call limits (e.g., 100,000/month per client)
   - **Why it matters**: Protects against:
     - DDoS attacks (overwhelming your service)
     - Runaway scripts (client's buggy code)
     - Cost overruns (LLM API calls are expensive)
   - **Implementation**: Cloud Endpoints or application-level throttling

3. **JWT Token Validation**: Every API request must include valid auth token
4. **CORS Policy**: Configure to allow app.servicios.palace.cl origin
5. **Input Validation**: Pydantic ensures all data matches expected format

#### 6.2.2 JWT Validation Implementation

**Every Backend Endpoint Protected**:
```python
# Every API endpoint MUST use this decorator
@require_auth
async def get_trades(request, user_context):
    # user_context automatically injected after JWT validation
    # Contains: organizationId, roles, email

    # All queries automatically filtered by organization
    trades = await db.trades.where(
        "organizationId", "==", user_context.organizationId
    ).get()
```

**What the @require_auth Decorator Does**:
1. **Extracts JWT** from Authorization header
2. **Validates signature** against Firebase public keys
3. **Checks expiration** (rejects if expired)
4. **Verifies issuer** (must be Firebase)
5. **Extracts claims** (organizationId, roles, etc.)
6. **Enforces multi-tenancy** (user can only access their org)
7. **Logs access** for audit trail
8. **Returns 401** if any validation fails

**Zero-Trust Principle**:
- Never trust the network location
- Never trust the user claims without validation
- Every request validated independently
- No assumptions about previous requests

#### 6.2.3 Secret Management
- **Secret Manager**: All credentials stored encrypted
- **Service Account Keys**: Minimal usage (Gmail API only)
- **API Keys**: Rotated quarterly
- **Database Credentials**: Using Application Default Credentials

### 6.3 Network Security

#### 6.3.1 Firewall Rules (Plain English)

**What These Rules Do**:
```yaml
What's Allowed:
- Web traffic (HTTPS) → Your app can receive user requests
- Internal services → Your backend services can talk to each other

What's Blocked:
- Direct server access → Hackers can't connect directly to your servers
- Remote login (SSH) → No one can remotely control servers (except emergencies)
```

**In Practice**:
- Users access through your web URL only
- All other access attempts are blocked
- Like having a single guarded entrance to a building

#### 6.3.2 Private Connectivity
- **Private Google Access**: Enabled for all subnets
- **Private Service Connect**: For third-party integrations
- **Cloud NAT**: Outbound internet access without external IPs

### 6.4 Compliance & Auditing

#### 6.4.1 Audit Logging

**Automatic Logging (GCP Provides)**:
- **Cloud Audit Logs**: Every GCP API call (who did what, when)
- **Cloud Run Logs**: HTTP requests, errors, performance
- **Firestore Audit**: Database reads/writes

**Application Logging (TO BE IMPLEMENTED)**:
**Status**: ⚠️ Not yet built - needs development
**Recommended Tool**: `structlog` for Python
- Structured JSON logs automatically sent to Cloud Logging
- Implementation required in all service files
- Example pattern to follow:
  ```python
  import structlog
  logger = structlog.get_logger()

  # Log user actions
  logger.info("trade.processed",
      user_id=user.id,
      trade_id=trade.id,
      action="confirmation_sent",
      client_id=client.id)
  ```

**What to Log**:
- User login/logout events
- Trade uploads and processing
- Email processing status
- Configuration changes
- API errors and exceptions

**Admin Log Viewer (Future Enhancement)**:
- Admin dashboard page for querying application logs
- Filter by: date range, user, action type, client
- Export capability for audit reports
- Real-time log streaming for debugging
- Implementation: Query Cloud Logging API via admin interface

#### 6.4.2 Compliance Standards
- **ISO 27001**: Required for Chilean/LATAM corporate clients
  - What companies expect for financial data handling
  - Demonstrates security maturity to enterprise clients

- **SOC 2 Type 2**: Future consideration only if expanding to US market
  - Primarily a North American requirement
  - Not typically requested in Latin America

- **Data Residency**: Primary in Chile (southamerica-west1)
  - Important for Chilean companies' data sovereignty requirements

- **Not Required**:
  - PCI DSS (no payment card processing)
  - GDPR (not targeting European market)

---

## 7. Integration Architecture

### 7.1 Email Integration (Gmail API)

#### 7.1.1 Configuration
**Development** (Current):
- **Service Account**: `gmail-email-processor@ccm-dev-pool.iam`
- **Mailbox**: `confirmaciones_dev@servicios.palace.cl`

**Production** (To Be Created):
- **Service Account**: `gmail-processor@prod1-svc-5q4z.iam`
- **Mailbox**: `confirmaciones@servicios.palace.cl`
- **Domain-Wide Delegation**: Required for palace.cl domain
- **Scopes**: `gmail.readonly`, `gmail.send`

#### 7.1.2 Email Monitoring Strategy

**Current (Development)**: 30-second polling - not scalable

**Production Approach - Gmail Push Notifications (Pub/Sub)**:
```
1. Gmail publishes new email event → Cloud Pub/Sub topic
2. Pub/Sub triggers Cloud Run endpoint immediately
3. Single processing per email (no race conditions)
4. Automatic retry on failure
5. Scales to handle concurrent emails
```

**Benefits**:
- Real-time processing (no polling delay)
- No duplicate processing
- Handles high volume automatically
- Cost-effective (pay per message, not constant polling)

#### 7.1.3 Email Processing Pipeline
```
1. Pub/Sub notification received
2. Fetch specific email (not bulk fetch)
3. Download attachments → Cloud Storage
4. Extract PDF content
5. Send to Vertex AI for data extraction
6. Store in Firestore
7. Trigger matching process
8. Queue automated response via Cloud Tasks
```

### 7.2 AI/LLM Integration

#### 7.2.1 Vertex AI Platform (Required for Production)

**Current Development**: Direct Claude API (needs migration)

**Production Configuration**:
- **Platform**: Google Vertex AI (us-east4 region)
- **Primary Model**: Claude Sonnet 4.5 via Vertex AI Model Garden
- **Fallback Model**: Gemini 2.5 Pro
- **Access Method**: Vertex AI Python SDK

**Why Vertex AI Instead of Direct API**:
- Unified billing and monitoring
- Better security (no API keys in code)
- Automatic fallback between models
- Request/response logging for compliance
- Rate limiting and quota management built-in

**Use Cases**:
- PDF parsing and trade data extraction
- Email content analysis
- Trade confirmation matching
- Discrepancy detection
- Multi-language content generation (ES/EN/PT)

### 7.3 SMS Integration

#### 7.3.1 Current Status
- **Development**: Initial research completed
- **Selected Provider**: MessageBird (to be implemented)

#### 7.3.2 MessageBird Configuration (Planned)

**Why MessageBird**:
- Simpler setup (no phone number rental required)
- Better Chilean carrier support
- Cost-effective: $0.04/SMS with no monthly fees
- Cleaner API for basic SMS sending
- Better reliability in Latin America

**Implementation** (Not yet coded):
```python
# Simple SMS sending
client.send_message(
    '+56912345678',  # Chilean mobile
    'Alerta: Discrepancia detectada en trade #12345'
)
```

**Use Cases** (When Implemented):
- Critical trade discrepancy alerts
- End-of-day settlement notifications
- System alerts (not for 2FA initially)

### 7.4 Central Bank of Chile Integration (Future Feature)

#### 7.4.1 Exchange Rate API
- **API Endpoint**: Banco Central de Chile public APIs
- **Data Retrieved**: Daily "Dólar Observado" exchange rate
- **Frequency**: Once daily at 7:00 PM Santiago time
- **Storage**: Historical rates in Firestore for reference

#### 7.4.2 Implementation
```python
# Scheduled Cloud Function (daily at 7 PM)
1. Call Banco Central API after market close
2. Parse USD/CLP exchange rate
3. Store in Firestore with timestamp
4. Calculate NDF settlement amounts
5. Cache until next update
```

**Purpose**:
- Calculate settlement amounts for USD/CLP NDF trades
- Track historical rates for valuation reports
- Support end-of-day mark-to-market calculations

### 7.5 Cloud Tasks Integration

#### 7.5.1 Queue Configuration
```python
Queues:
- email-queue:      # Automated email sending
    rate: 100/s
    max_concurrent: 100
    retry_config: exponential backoff

- priority-queue:   # Time-sensitive operations
    rate: 500/s
    max_concurrent: 500

- general-queue:    # Background processing
    rate: 50/s
    max_concurrent: 50

- file-sync-queue:  # Automatic trade file synchronization
    rate: 10/s
    max_concurrent: 5
    retry_config: exponential backoff, max 3 attempts
```

### 7.6 Automatic Trade File Synchronization

#### 7.6.1 Overview
Automated synchronization of trade CSV files from client-provided secure locations, eliminating manual upload requirements.

#### 7.6.2 Supported File Sources

**Priority 1: Cloud Storage** (Recommended):
```yaml
Google Cloud Storage:
  URL: gs://client-bucket/trades/
  Auth: Workload Identity Federation (no passwords)

AWS S3:
  URL: s3://client-bucket/trades/
  Auth: IAM role or access keys

Azure Blob Storage:
  URL: https://account.blob.core.windows.net/trades/
  Auth: SAS token or service principal
```

**Priority 2: SFTP** (Legacy support):
```yaml
SFTP Server:
  URL: sftp://ftp.client.com/trades/
  Auth: Username/password (stored in Secret Manager)
  Port: 22 (configurable)
```

#### 7.6.3 Sync Configuration (Per Client)

**Firestore Schema**:
```typescript
/clients/{clientId}/syncConfig
  - enabled: boolean
  - sourceType: 'gcs' | 's3' | 'azure' | 'sftp'
  - sourceUrl: string
  - credentialsRef: string  // Secret Manager reference
  - schedule: {
      frequency: number     // minutes (default: 10)
      startHour: number    // 24hr format (default: 8)
      endHour: number      // 24hr format (default: 20)
      timezone: string     // 'America/Santiago'
    }
  - filePattern: string    // e.g., "trades_*.csv"
  - lastSyncTime: timestamp
  - lastSyncStatus: 'success' | 'failed' | 'in_progress'
```

#### 7.6.4 File Processing Logic

**Detection Strategy**:
```python
1. Check source every 10 minutes (configurable)
2. List all files matching pattern (e.g., trades_*.csv)
3. Compare file timestamps with lastSyncTime
4. Download new/modified files since last sync
5. Process immediately upon detection
```

**Trade Update Rules**:
```python
For each synced file:
  1. Parse CSV and validate format
  2. For each trade in file:
     - If trade exists and MATCHED/CONFIRMED → Skip (no update)
     - If trade exists and UNMATCHED → Update with new data
     - If trade doesn't exist → Create new trade
  3. Mark all trades from this sync with uploadSessionId
  4. Log sync activity for audit trail
```

**Data Retention**:
- Keep all file versions downloaded during current day
- End of day: Delete old versions, keep only latest
- Maintain sync history for 30 days

#### 7.6.5 Implementation Architecture

**Sync Trigger Flow**:
```
Cloud Scheduler (every 10 min) → Cloud Run endpoint
                                      ↓
                            Check if within sync hours
                                      ↓
                              For each enabled client:
                                      ↓
                            Queue sync task → Cloud Tasks
                                      ↓
                              Execute file sync:
                              1. Connect to source
                              2. List files
                              3. Download new/modified
                              4. Process trades
                              5. Update lastSyncTime
```

**Manual Trigger**:
```
User clicks "Sync Now" → API call → Bypass schedule check → Queue sync task
```

#### 7.6.6 Security Configuration

**Secret Storage Structure**:
```yaml
Secret Manager:
  client-123-sync-creds:
    type: "sftp"
    username: "client123_user"
    password: "encrypted_password"

  client-456-sync-creds:
    type: "s3"
    access_key_id: "AKIA..."
    secret_access_key: "encrypted_key"

  client-789-sync-creds:
    type: "gcs"
    # Empty - uses Workload Identity
```

**Security Best Practices**:
1. **Credentials Management**:
   - All passwords encrypted in Secret Manager
   - Access limited to sync service account only
   - Audit logging of all credential access

2. **Network Security**:
   - SFTP connections use SSH key when possible
   - All transfers over encrypted channels (TLS/SSH)
   - IP allowlisting where supported

3. **Access Patterns**:
   - Read-only access to client directories
   - No ability to delete/modify source files
   - Download to temporary Cloud Storage, then process

**Future Enhancement - Workload Identity** (When clients use GCS):
```python
# No credentials needed - pure IAM
# Client grants: storage.objectViewer to ccm-sync@prod1-svc-5q4z.iam
storage_client = storage.Client()
bucket = storage_client.bucket('client-bucket')
```

#### 7.6.7 Monitoring & Alerts

**Key Metrics**:
- Files synced per client
- Sync success/failure rates
- Processing time per file
- New trades created vs updated

**Alert Conditions**:
- Sync fails 3 times consecutively
- No new files for 24 hours (if expected)
- File format validation errors
- Credential authentication failures

#### 7.6.8 Client Onboarding Process

**For Palace Admin**:
1. Client provides: Source URL, credentials, file pattern
2. Admin creates Secret Manager entry
3. Admin configures sync in client settings
4. Test manual sync
5. Enable scheduled sync

**For Client**:
- View sync status in dashboard
- Trigger manual sync anytime
- Receive notifications of sync results
- Download sync activity reports

---

## 8. Deployment Architecture

### 8.1 Container Strategy

#### 8.1.1 Backend Container
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
USER app
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 8.1.2 Cloud Run Configuration Explained

**What Cloud Run Does**:
- Runs your containerized backend
- Automatically manages servers (you never see them)
- Scales up/down based on traffic
- Only charges when processing requests

**Recommended Configuration** (Pre-Production through Early Production):
```yaml
Service: ccm-backend
Region: southamerica-west1
CPU: 1                    # 1 CPU is fine for early production too
Memory: 2Gi              # Sufficient for PDF processing
Min Instances: 0         # CRITICAL: Scale to zero = $0 when idle!
Max Instances: 10        # Can handle ~500 concurrent users
Concurrency: 50          # Requests each instance handles
Timeout: 60s             # Long enough for LLM API calls
```

**Why Min Instances = 0 is Perfect for You**:
- **Nights/Weekends**: Service shuts down completely → **$0 cost**
- **First morning request**: Takes ~10 seconds to start ("cold start")
- **Subsequent requests**: Fast (instance already running)
- **Monthly savings**: 80-90% cheaper than always-on
- **Acceptable trade-off**: 10-second delay on first request is fine

**Cold Start Management (Production Only)**:
```yaml
# Cloud Scheduler warm-up job
Name: ccm-warmup
Schedule: "*/10 7-18 * * 1-5"  # Every 10 min, 7 AM-6 PM, Mon-Fri
Timezone: America/Santiago
Target: https://servicios.palace.cl/api/health
Method: GET

# Result: Service stays warm during business hours
# Cost: ~$0.50/month
# Benefit: No cold starts for clients
```

**When to Consider Scaling Up**:
```yaml
Keep CPU: 1          # Until processing takes >5 seconds regularly
Keep Memory: 2Gi     # Until handling files >50MB
Keep Min: 0          # Until cold starts annoy paying clients
Increase Max: 10→50  # When you have >100 concurrent users
```

**Real Cost Comparison**:
- **Your current dev environment**: ~$10/month
- **With Min=0 (recommended)**: ~$10-30/month
- **With Min=2 (always on)**: ~$100+/month
- **Early production recommendation**: Use exact same settings as pre-production!

### 8.2 Pub/Sub Configuration (Gmail Integration)

#### 8.2.1 Gmail Push Notifications Setup
```yaml
Topic: gmail-notifications
Subscription: gmail-processor
Push Endpoint: https://ccm-backend-prod.run.app/api/v1/gmail/webhook
Acknowledgment Deadline: 60 seconds
Retry Policy: Exponential backoff, max 5 attempts
```

#### 8.2.2 Gmail Watch Configuration
```python
# One-time setup per mailbox
gmail_service.users().watch(
    userId='confirmaciones@servicios.palace.cl',
    body={
        'topicName': 'projects/prod1-svc-5q4z/topics/gmail-notifications',
        'labelIds': ['INBOX']
    }
).execute()
# Renew every 7 days via Cloud Scheduler
```

### 8.3 Frontend Deployment

#### 8.3.1 Build Process
```bash
# Production build
npm run build

# Deploy to Firebase
firebase deploy --only hosting:production
```

#### 8.3.2 Firebase Hosting Configuration
```json
{
  "hosting": {
    "public": "build",
    "rewrites": [{
      "source": "/api/**",
      "function": "api"
    }],
    "headers": [{
      "source": "**/*.@(jpg|jpeg|gif|png|svg|webp|js|css|eot|otf|ttf|ttc|woff|woff2|font.css)",
      "headers": [{
        "key": "Cache-Control",
        "value": "max-age=31536000"
      }]
    }]
  }
}
```

### 8.4 CI/CD Pipeline

#### 8.4.1 Current Status
**Manual Deployment** (What you're doing now):
- Push code to GitHub
- Manually deploy to Cloud Run via Console
- Manually deploy frontend to Firebase

#### 8.4.2 Recommended CI/CD Setup (When Ready)

**What CI/CD Does**:
- Automatically deploys when you push to GitHub
- Runs tests first (blocks deploy if tests fail)
- Zero-downtime deployments
- Rollback on errors

**Simple GitHub Actions Workflow**:
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]    # Trigger on push to main

jobs:
  deploy-backend:
    steps:
      1. Run Python tests
      2. Build Docker image
      3. Push to Google Artifact Registry
      4. Deploy to Cloud Run (automatic!)

  deploy-frontend:
    steps:
      1. Run React tests
      2. Build production bundle
      3. Deploy to Firebase Hosting
```

**Cost**: GitHub Actions free for public repos, 2000 minutes/month for private

**When to Implement**: Once you have paying clients (manual is fine for now)

### 8.5 Infrastructure as Code

#### 8.5.1 Current Status
**Note**: Terraform structure exists from Google Cloud Foundation setup but no custom modules yet built.

#### 8.5.2 Proposed Terraform Modules (Future)
```hcl
modules/
├── networking/     # Already exists from Foundation
├── compute/        # TO DO: Cloud Run services
├── storage/        # TO DO: Cloud Storage buckets
├── database/       # TO DO: Firestore configuration
├── security/       # Already exists (KMS from Foundation)
└── monitoring/     # TO DO: Alerts and dashboards
```

**Why Infrastructure as Code Matters**:
- **Repeatability**: Deploy same config to staging/production
- **Version Control**: Track all infrastructure changes in Git
- **Disaster Recovery**: Rebuild everything from code if needed
- **Compliance**: Auditors love documented infrastructure

**For Now**: Manual deployment via Console is fine for pre-production

---

## 9. Networking & Connectivity

### 9.1 Domain Configuration (Using palace.cl)

#### 9.1.1 Production Setup with Load Balancer

**Your URLs**:
```
Frontend Application: https://app.servicios.palace.cl
Backend API: https://api.servicios.palace.cl
```

**Architecture Components**:

1. **Frontend - Firebase Hosting**:
   ```bash
   # Firebase Console → Hosting
   1. Add custom domain: "app.servicios.palace.cl"
   2. Update DNS:
      CNAME: app.servicios → ccm-prod.web.app
   3. SSL certificate auto-provisioned by Firebase
   ```

2. **Backend - Global Load Balancer**:
   ```yaml
   Load Balancer Configuration:
     Name: ccm-api-lb
     Type: HTTPS Load Balancer
     Frontend:
       IP: Static IP (reserved)
       Port: 443
       Certificate: Google-managed SSL for api.servicios.palace.cl
     Backend:
       Service: Cloud Run (ccm-backend)
       Region: southamerica-west1
     Security:
       Cloud Armor Policy: ccm-ip-whitelist
   ```

3. **DNS Configuration**:
   ```
   app.servicios.palace.cl → CNAME → Firebase Hosting
   api.servicios.palace.cl → A Record → Load Balancer IP
   ```

**Cost Breakdown**:
- Load Balancer: $25/month (minimum)
- Static IP: $3/month
- Cloud Armor: Included with Load Balancer
- SSL Certificates: Free (Google-managed)
- **Total: ~$28/month for enterprise-grade security**

#### 9.1.2 Why Load Balancer is Worth It

**Security Benefits**:
- ✅ IP whitelisting at network edge (Cloud Armor)
- ✅ DDoS protection included
- ✅ WAF rules capability
- ✅ ISO 27001 compliant architecture

**Operational Benefits**:
- ✅ Centralized security management
- ✅ Professional setup clients expect
- ✅ Better monitoring and logging
- ✅ Easy to add CDN later if needed

### 9.2 Network Security

**IP Whitelisting via Cloud Armor**:
- Enforced at Load Balancer level
- Only whitelisted client IP ranges can access API
- Configure per client organization in Cloud Armor policy
- Blocks unauthorized access attempts at network edge

**Network Paths**:
```
Frontend Path:
Client Browser → app.servicios.palace.cl → Firebase Hosting → React SPA

API Path:
Client Browser → api.servicios.palace.cl → Cloud Armor (IP Check)
                                                ↓ (If allowed)
                                          Load Balancer → Cloud Run
```

---

## 10. Monitoring & Observability (Simplified for Pre-Production)

### 10.1 What You Get for FREE

#### 10.1.1 Cloud Run Metrics (Automatic)
**No setup required - just look at the console**:
- ✅ Is service up? (uptime indicator)
- ✅ Request count and latency
- ✅ Error rate (4xx, 5xx responses)
- ✅ Container instances (scaling behavior)
- ✅ Memory and CPU usage

**Where to see it**: Cloud Console → Cloud Run → Your Service → Metrics tab

#### 10.1.2 Cloud Logging (Free up to 50GB/month)
**What's automatically logged**:
- All Python `print()` statements
- HTTP request/response logs
- Error stack traces
- Container start/stop events

**Where to see it**: Cloud Console → Logging → Logs Explorer

#### 10.1.3 Error Reporting (Free)
**Automatically groups and tracks**:
- Python exceptions
- HTTP 500 errors
- Crashed container events

**Where to see it**: Cloud Console → Error Reporting

### 10.2 Simple Monitoring Strategy

#### 10.2.1 What to Actually Monitor (Pre-Production)
```yaml
Daily Checks:
- Any errors in Error Reporting? Fix them
- Billing on track? (< $100/month)

After Each Deploy:
- Service still responding? Test it
- Any new errors? Check Error Reporting

Weekly:
- Check Cloud Run metrics for trends
- Review costs in Billing
```

#### 10.2.2 Single Alert That Matters
**Budget Alert** (Already set in Section 13):
- Alert when monthly spend exceeds $80
- That's it! No complex alerting needed yet

### 10.3 When to Add More Monitoring

**Add monitoring when**:
- You have paying clients (need uptime alerts)
- You can't figure out why something broke
- You're spending too much time debugging

**Future Enhancements** (Not now):
- Custom dashboards
- PagerDuty integration
- APM tools (DataDog, New Relic)
- Distributed tracing


---

## 11. Disaster Recovery & Business Continuity (Simplified for Pre-Production)

### 11.1 Current Disaster Recovery (Simple & Effective)

#### 11.1.1 What Could Go Wrong & How to Recover

**"I deployed bad code"** (Most likely):
- **Solution**: Cloud Run instant rollback
- **How**: Console → Cloud Run → Revisions → "Roll back"
- **Recovery time**: 30 seconds
- **Cost**: Free

**"I accidentally deleted data"** (Happens to everyone):
- **Solution**: Manual backup before risky changes
- **How**:
  ```bash
  # Before making big changes
  gcloud firestore export gs://ccm-backups/backup-$(date +%Y%m%d)
  ```
- **Recovery time**: 1-2 hours
- **Cost**: ~$0.05 per backup

**"Google Cloud is down"** (Rare):
- **Solution**: Wait for Google
- **Expected downtime**: ~20 minutes/month
- **Your cost**: $0 (not your problem)

#### 11.1.2 Your Current DR Assets

**Already Protected**:
- ✅ **Code**: GitHub (version control)
- ✅ **Deployments**: Cloud Run keeps 100 revisions
- ✅ **Configs**: In this documentation
- ✅ **Secrets**: In Secret Manager (versioned)

**Manual Backup Process** (Do this weekly):
```bash
# 1. Export Firestore
gcloud firestore export gs://ccm-backups/weekly-$(date +%Y%m%d)

# 2. Verify backup completed
gcloud firestore operations list

# 3. Document any config changes in Git
```

### 11.2 When to Add Enterprise DR (Future)

#### 11.2.1 Signs You Need More DR
- Clients demand 99.9% uptime SLAs
- Downtime costs > $1000/hour
- Processing real money transactions
- Regulatory compliance requirements

#### 11.2.2 What Enterprise DR Would Add
- Automated daily backups ($10/month)
- Cross-region replication ($50/month)
- Automated failover ($100+/month)
- Regular DR testing

### 11.3 Pre-Production DR Checklist

**Weekly**:
- [ ] Manual Firestore backup
- [ ] Verify backup completed
- [ ] Test you can restore (quarterly)

**Before Major Changes**:
- [ ] Take backup
- [ ] Document what you're changing
- [ ] Have rollback plan ready

**Cost**: ~$1/month for backup storage

---

## 12. Scalability & Performance (Pre-Production Reality)

### 12.1 What Scales Automatically (No Work Needed)

#### 12.1.1 Services That "Just Scale"
**Cloud Run**:
- 0 users → 0 instances (costs $0)
- 10 users → 1 instance
- 100 users → 2-3 instances
- 1000 users → 10+ instances
- **You don't configure anything!**

**Firestore**:
- Handles 10,000 writes/second out of the box
- No configuration needed
- Just works

**Firebase Hosting**:
- Global CDN included
- Millions of requests? No problem
- Zero configuration

#### 12.1.2 Current Scale Reality
```yaml
Your Current Scale:
- Users: 0 (pre-production)
- Daily requests: ~100 (testing)
- Database size: < 100MB
- Monthly cost target: < $100

What This Handles:
- Up to 500 concurrent users
- Up to 10,000 requests/day
- Up to 10GB database
- All within your budget
```

### 12.2 Performance That Matters Now

#### 12.2.1 What's Actually Slow
**Can't Fix** (Accept it):
- LLM API calls: 1-3 seconds (Vertex AI/Claude)
- Cold starts: 10 seconds (solved with scheduler)

**Might Need Optimization** (Later):
- Large PDF processing (but you said PDFs are small)
- Complex trade matching (not an issue yet)

#### 12.2.2 What's Already Fast
- Database queries: < 50ms
- Static files: CDN cached
- Simple API calls: < 200ms
- Authentication: < 100ms

### 12.3 When to Think About Performance

#### 12.3.1 Scaling Triggers
```yaml
Ignore Until:
- 100+ concurrent users
- 10,000+ trades/day
- Database > 1GB
- LLM costs > $500/month

Then Consider:
- Increasing Cloud Run max instances
- Adding database indexes
- Caching frequent queries
- Optimizing LLM prompts
```

#### 12.3.2 Pre-Production Performance Checklist
**Don't Do**:
- ❌ Load testing (no load yet)
- ❌ Caching layers (unnecessary complexity)
- ❌ Database sharding (overkill)
- ❌ Performance optimization (nothing is slow)

**Do Focus On**:
- ✅ Building features
- ✅ Getting clients
- ✅ Fixing actual bugs
- ✅ Monitoring costs

---

## 13. Cost Optimization

### 13.1 Resource Optimization

#### 13.1.1 Committed Use Discounts
- **Compute**: 1-year commitment for base capacity
- **Storage**: Committed use for Firestore and Cloud Storage

#### 13.1.2 Auto-scaling Policies
- **Development**: Scale to zero during off-hours
- **Production**: Scale to zero with Cloud Scheduler warm-up during business hours

### 13.2 Service-Specific Costs

#### 13.2.1 Pub/Sub (Gmail Integration)
- **Messages**: $0.40 per million
- **Expected Volume**: ~10,000 emails/month = $0.004/month
- **Negligible cost** for email notifications

#### 13.2.2 Key Service Pricing
```yaml
Estimated Monthly Costs (Production with IP Whitelisting):
- Load Balancer: $25 (required for Cloud Armor)
- Static IP: $3 (for api.servicios.palace.cl)
- Cloud Run: ~$20 (minimal instances, scale to zero)
- Firestore: ~$10 (small data volume initially)
- Cloud Storage: ~$5 (documents/attachments)
- Vertex AI: ~$50 (LLM usage for production)
- Pub/Sub: < $1 (email notifications)
- Cloud Tasks: < $1 (async processing)
- Total: ~$115/month for production with enterprise security
```

**Cost Note**: The $28/month for Load Balancer + IP is the price of professional security. One client easily covers this.

### 13.3 Cost Monitoring

#### 13.3.1 Realistic Budget Alerts
```yaml
Monthly Budgets (Pre-Production):
- Development: $100 (alert at 80%)
- First Production Deploy: $300 (alert at 80%)
- Growth Phase: Scale with revenue
```

#### 13.3.2 Cost Allocation
- **Labels**: Environment, service
- **Export**: BigQuery for detailed analysis

---

## 14. Migration Path

### 14.1 Development to Production Checklist

#### Phase 1: Infrastructure Setup
- [ ] Use existing production project (prod1-svc-5q4z)
- [ ] Verify networking already configured from Foundation
- [ ] Confirm CMEK encryption enabled
- [ ] Create production service accounts

#### Phase 2: Data Migration
- [ ] Export development Firestore data
- [ ] Create production Firestore database with CMEK
- [ ] Import and validate data
- [ ] Test backup/restore process

#### Phase 3: Application Deployment
- [ ] Deploy backend to Cloud Run (use same config as dev)
- [ ] Configure Firebase Hosting with servicios.palace.cl
- [ ] Set up API routing through Firebase
- [ ] Test end-to-end flow

#### Phase 4: Integration Setup
- [ ] Create production Gmail service account
- [ ] Configure Pub/Sub for email notifications
- [ ] Set up Gmail watch on confirmaciones@servicios.palace.cl
- [ ] Configure Cloud Tasks queues
- [ ] Add secrets to Secret Manager
- [ ] Set up budget alerts

#### Phase 5: Testing & Validation
- [ ] Test email processing flow
- [ ] Test trade upload and matching
- [ ] Verify authentication works
- [ ] Check all language translations
- [ ] Confirm automated emails work

#### Phase 6: Go-Live
- [ ] Update DNS for servicios.palace.cl
- [ ] Configure Cloud Scheduler for warm-up
- [ ] Monitor for first 48 hours
- [ ] Document any issues found

**Note**: No timeframes specified - move at your own pace based on priorities and available time.

---

## Appendices

### A. Environment Variables

```bash
# Production Environment Variables
PROJECT_ID=prod1-service
FIRESTORE_DATABASE=ccm-production
FIREBASE_AUTH_DOMAIN=ccm-prod.firebaseapp.com
GMAIL_SERVICE_EMAIL=confirmaciones@servicios.palace.cl
CLAUDE_API_KEY=[encrypted in Secret Manager]
MESSAGEBIRD_API_KEY=[encrypted in Secret Manager]
CLOUD_TASKS_LOCATION=us-east4
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### B. Security Checklist

- [ ] CMEK encryption enabled for all data stores
- [ ] Service account keys minimized (Gmail only)
- [ ] Network security policies applied
- [ ] API authentication required on all endpoints
- [ ] Rate limiting configured
- [ ] DDoS protection enabled
- [ ] Audit logging enabled
- [ ] Secret rotation schedule configured
- [ ] Backup and recovery tested
- [ ] Security assessment completed

### C. Monitoring Dashboards

1. **Operations Dashboard**
   - Service health status
   - Request rates and latencies
   - Error rates by service
   - Active users

2. **Business Dashboard**
   - Trades processed
   - Emails processed
   - Match success rates
   - Client activity

3. **Infrastructure Dashboard**
   - Resource utilization
   - Network traffic
   - Storage growth
   - Cost trends

### D. Contact Information

**Development Team**
- Technical Lead: [TBD]
- DevOps: [TBD]
- Security: [TBD]

**Operations**
- 24/7 Support: [TBD]
- Escalation: [TBD]

---

## Document Control

**Review Schedule**: Quarterly
**Next Review**: January 2026
**Owner**: Palace.cl Engineering Team
**Distribution**: Engineering, Operations, Security Teams

---

*This document represents the complete production architecture for CCM 2.0 as of October 2025. It should be updated as the system evolves and new requirements emerge.*