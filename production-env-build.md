# CCM 2.0 Production Environment Build Log

## Document Purpose
This document records the ACTUAL steps taken to build the production environment for CCM 2.0, including any deviations from the planned architecture.

**Started:** October 17, 2025
**Builder:** Ben Clark with Claude assistance
**Target Environment:** prod1-svc-5q4z (Production)
**ISO 27001 Relevance:** Critical - Documents production security controls

---

## Build Status

| Component | Status | Date | Notes |
|-----------|--------|------|-------|
| KMS Setup | ✅ Complete | Oct 17 | Keyring and key created |
| Firestore Database | 🚫 Blocked | Oct 17 | Awaiting CMEK allowlist approval |
| Cloud Run Backend | 🚫 Blocked | | Depends on Firestore |
| Static IP | ✅ Complete | Oct 17 | 34.0.58.187 allocated |
| Load Balancer | 🚫 Blocked | | Needs Cloud Run backend first |
| Cloud Armor | 🚫 Blocked | | Needs Load Balancer first |
| Firebase Frontend | ✅ Deployed | Oct 17 | Live at prod1-svc-5q4z.web.app |
| DNS Configuration | ⏳ Ready | | Records documented, awaiting backend |
| Vanta Connection | 🚫 Blocked | | Needs complete services |

---

## Step-by-Step Build Process

### Step 1: KMS Setup for CMEK Encryption

**Reference Design:** [production-architecture.md Section 5.3](production-architecture.md#53-data-encryption)
**Approach:** Manual setup (not using Autokey)
**Reason:** Better control and understanding for ISO 27001 compliance

#### 1.1 Verify KMS Project Setup

**Command Run:**
```bash
# Check existing keyrings in production KMS project
gcloud kms keyrings list --location=southamerica-west1 --project=kms-proj-g5c6fwjtocz9
```

**Result:**
- No keyrings found (empty project)
- Need to create from scratch

**Reference from Dev:**
```bash
# Development has this structure:
# Keyring: dev-ccm-keyring
# Key: firestore-dev-key
```

#### 1.2 Create Production Keyring

**Planned Command:**
```bash
gcloud kms keyrings create prod-ccm-keyring \
  --location=southamerica-west1 \
  --project=kms-proj-g5c6fwjtocz9
```

**Result:** ✅ Keyring already existed (found during execution)
**Verified:** `prod-ccm-keyring` exists with 0 keys
**Date:** October 17, 2025

#### 1.3 Create Firestore Encryption Key

**Planned Command:**
```bash
gcloud kms keys create firestore-prod-key \
  --location=southamerica-west1 \
  --keyring=prod-ccm-keyring \
  --purpose=encryption \
  --project=kms-proj-g5c6fwjtocz9
```

**Result:** ✅ Key created successfully
**Key Name:** firestore-prod-key
**Purpose:** ENCRYPT_DECRYPT
**State:** ENABLED
**Date:** October 17, 2025

#### 1.4 Grant Firestore Service Account Permissions

**Project Number Found:** 1087797777595
**Service Account:** service-1087797777595@gcp-sa-firestore.iam.gserviceaccount.com

**Command Attempted:**
```bash
gcloud kms keys add-iam-policy-binding firestore-prod-key \
  --location=southamerica-west1 \
  --keyring=prod-ccm-keyring \
  --member=serviceAccount:service-1087797777595@gcp-sa-firestore.iam.gserviceaccount.com \
  --role=roles/cloudkms.cryptoKeyEncrypterDecrypter \
  --project=kms-proj-g5c6fwjtocz9
```

**Result:** ⚠️ Service account doesn't exist yet
**Issue:** Firestore service account is only created when first database is created
**Solution:** Need to create database first, then grant permissions
**Date:** October 17, 2025

---

### Step 2: Firestore Database Creation

**Reference Design:** [production-architecture.md Section 5.1](production-architecture.md#51-database-design-firestore)
**Database Name:** ccm-production
**Location:** southamerica-west1
**Encryption:** CMEK with key from Step 1

**Planned Command:**
```bash
gcloud firestore databases create ccm-production \
  --location=southamerica-west1 \
  --type=firestore-native \
  --project=prod1-svc-5q4z
  # Note: CMEK might need to be configured separately after creation
```

**Result:** ✅ Database created (without CMEK)
**Database Name:** ccm-production
**Location:** southamerica-west1
**UID:** 9d91a849-d0b2-4efb-bc6e-3503a22c70d3
**CMEK Status:** ❌ Not enabled (cannot add after creation)
**Date:** October 17, 2025

---

### Step 3: CMEK Database Allowlist Request

**Status:** ✅ SUBMITTED - Awaiting Google Approval

**Form URL:** https://forms.gle/D3cB7xY6A44aVusY9
**Submission Date:** October 17, 2025
**Case Reference:** Organization ID 165254678508 requested org-level CMEK enablement

**Information Submitted:**
```
Project ID: prod1-svc-5q4z
Project Number: 1087797777595
Organization ID: 165254678508
Database Name: ccm-production
Region: southamerica-west1
Database Type: Firestore Native
KMS Key Path: projects/kms-proj-g5c6fwjtocz9/locations/southamerica-west1/keyRings/prod-ccm-keyring/cryptoKeys/firestore-prod-key
Business Justification: ISO 27001 compliance requirement for production environment handling financial trade data
Contact Email: ben.clark@palace.cl
```

**Check Status Command:**
```bash
# Test if CMEK database creation is enabled (run daily)
gcloud firestore databases create test-cmek \
  --location=southamerica-west1 \
  --type=firestore-native \
  --cmek-key-name=projects/kms-proj-g5c6fwjtocz9/locations/southamerica-west1/keyRings/prod-ccm-keyring/cryptoKeys/firestore-prod-key \
  --project=prod1-svc-5q4z \
  --async
```

**Expected Timeline:**
- Form submission: ✅ October 17, 2025
- Google response: Expected by October 19, 2025 (48 hours)
- Alternative: Open P2 support case if no response by October 20

**Next Steps After Approval:**
1. Receive confirmation email from Google
2. Delete temporary non-CMEK database
3. Create CMEK-encrypted database
4. Continue with production deployment

---

## Step 4: Tasks While Waiting for CMEK Approval

### 4.1 Reserve Static IP for Load Balancer

**Purpose:** Reserve the production static IP that will be used for api.servicios.palace.cl

**Commands Executed:**
```bash
# Reserve external static IP for production
gcloud compute addresses create ccm-prod-lb-ip \
  --region=southamerica-west1 \
  --network-tier=STANDARD \
  --project=prod1-svc-5q4z

# View the allocated IP
gcloud compute addresses describe ccm-prod-lb-ip \
  --region=southamerica-west1 \
  --project=prod1-svc-5q4z --format="value(address)"
```

**Result:** ✅ Complete - October 17, 2025
**Static IP Allocated:** **34.0.58.187**
**Region:** southamerica-west1
**Network Tier:** STANDARD
**Resource Name:** ccm-prod-lb-ip

### 4.2 Set Up Firebase Hosting

**Purpose:** Prepare Firebase Hosting for the frontend deployment

**Actions Completed:**

1. **Added Firebase to GCP Project:**
```bash
firebase projects:addfirebase prod1-svc-5q4z
```

2. **Created firebase.json** with:
   - Site: `prod1-svc-5q4z`
   - Public directory: `build` (corrected from dist)
   - Single-page app rewrites configured
   - Security headers (X-Frame-Options, X-Content-Type-Options, etc.)

3. **Created .firebaserc** with:
   - Default project: prod1-svc-5q4z
   - Production alias: prod1-svc-5q4z

4. **Enabled Firebase Hosting API:**
```bash
gcloud services enable firebasehosting.googleapis.com --project=prod1-svc-5q4z
```

5. **Built and Deployed Frontend:**
```bash
cd frontend
npm run build  # Build completed with warnings (unused variables)
firebase deploy --only hosting --project=prod1-svc-5q4z
```

**Result:** ✅ DEPLOYED - October 17, 2025
**Hosting URL:** https://prod1-svc-5q4z.web.app
**Custom Domain:** Will map to app.servicios.palace.cl (DNS not configured yet)
**Note:** Frontend deployed but will show errors until backend is deployed

### 4.3 Prepare DNS Records

**Purpose:** Document the DNS changes needed for production

**Records to Add (when ready):**
```
Type: A
Name: api.servicios.palace.cl
Value: 34.0.58.187
TTL: 300

Type: CNAME
Name: app.servicios.palace.cl
Value: prod1-svc-5q4z.web.app
TTL: 300
```

**Status:** ✅ Documented - October 17, 2025
**Static IP:** 34.0.58.187 (allocated in step 4.1)
**Note:** Do not configure DNS until Load Balancer is fully set up

### 4.4 Prepare Cloud Armor Security Policy

**Purpose:** Define IP whitelist policy for production

**Policy Configuration:**
```yaml
name: ccm-prod-security-policy
description: IP whitelist for CCM production
rules:
  - priority: 1000
    match:
      srcIpRanges:
        - "181.43.144.17/32"  # Palace Office
        - "186.10.23.45/32"   # Ben's home
    action: allow
  - priority: 2147483647
    match:
      srcIpRanges:
        - "*"
    action: deny(403)
```

**Status:** ⏳ Ready to create after Load Balancer
**Dependencies:** Load Balancer must exist first

---

## Deviation Log

| Step | Planned | Actual | Reason |
|------|---------|--------|--------|
| KMS Setup | Use Autokey | Manual creation | Better control for ISO 27001 |
| Firestore | Direct CMEK creation | Need allowlist first | Google CMEK quota limit |
| Org Policy | Keep enabled | Temporarily disabled | Workaround for database creation |

---

## Testing Checklist

- [ ] KMS keyring created successfully
- [ ] Encryption key accessible
- [ ] Firestore can use the encryption key
- [ ] Database created with CMEK
- [ ] Can write/read from database

---

## Notes & Lessons Learned

- Starting with manual KMS setup instead of Autokey for better understanding
- Need to document each step for ISO 27001 audit trail

---

## Next Steps

1. Complete KMS setup
2. Create Firestore database
3. Deploy backend to Cloud Run
4. Continue with remaining components