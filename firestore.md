# Firestore Database Setup - Client Confirmation Manager

## 🎯 **Project Overview**

This document tracks the setup and configuration of Firestore database for the Client Confirmation Manager (CCM2) application within the `palace.cl` GCP organization.

## 📋 **Setup Progress**

### ✅ **Completed Steps**

#### 1. GCP Development Project Creation
- **Project Name**: CCM2 - Dev Pool
- **Project ID**: `ccm-dev-pool`
- **Project Number**: 1075260378031
- **Location**: Development folder (ID: 802429588971) in `palace.cl` organization
- **Created**: August 3, 2025

**Command Used:**
```bash
gcloud projects create ccm-dev-pool \
    --name="CCM2 - Dev Pool" \
    --folder=802429588971 \
    --set-as-default
```

#### 2. Required APIs Enabled
- ✅ Cloud Resource Manager API
- ✅ Firestore API (`firestore.googleapis.com`)
- ✅ Firebase API (`firebase.googleapis.com`)  
- ✅ Cloud Functions API (`cloudfunctions.googleapis.com`)
- ✅ Secret Manager API (`secretmanager.googleapis.com`)
- ✅ Cloud KMS API (`cloudkms.googleapis.com`)

**Command Used:**
```bash
gcloud services enable firestore.googleapis.com \
    firebase.googleapis.com \
    cloudfunctions.googleapis.com \
    secretmanager.googleapis.com \
    cloudkms.googleapis.com \
    --project=ccm-dev-pool
```

#### 3. Customer-Managed Encryption Keys (CMEK) Setup
**KMS Project Identified**: `kms-proj-nqs0vivc9gcm` (in Development folder)

**Encryption Key Created:**
- **Keyring**: `dev-ccm-keyring`
- **Key Name**: `firestore-dev-key`
- **Location**: `southamerica-west1`
- **Purpose**: Encryption

**Commands Used:**
```bash
# Create keyring in dedicated KMS project
gcloud kms keyrings create dev-ccm-keyring \
    --location=southamerica-west1 \
    --project=kms-proj-nqs0vivc9gcm

# Create encryption key
gcloud kms keys create firestore-dev-key \
    --keyring=dev-ccm-keyring \
    --location=southamerica-west1 \
    --purpose=encryption \
    --project=kms-proj-nqs0vivc9gcm
```

**Full Key Path:**
```
projects/kms-proj-nqs0vivc9gcm/locations/southamerica-west1/keyRings/dev-ccm-keyring/cryptoKeys/firestore-dev-key
```

## 🔐 **Organization Policy Constraints**

### **Security Requirements**
Your `palace.cl` organization has strict security policies that require:

1. **`constraints/gcp.restrictNonCmekServices`**: All services must use Customer-Managed Encryption Keys
2. **`constraints/gcp.restrictCmekCryptoKeyProjects`**: CMEK keys must come from dedicated KMS projects

### **Impact**
- Cannot use Google-managed encryption for any services
- Must use CMEK from the dedicated KMS project: `kms-proj-nqs0vivc9gcm`
- Firestore requires Google's manual allowlist approval for CMEK usage

## 📝 **CMEK Allowlist Request Status**

### **Request Submitted**: August 3, 2025

**Details Submitted:**
- **Project ID**: `ccm-dev-pool`
- **Product**: Firestore
- **Number of Databases (12 months)**: 5-10
- **Business Justification**: Multi-tenant SaaS platform for Chilean banking industry requiring customer-controlled encryption for financial services compliance. Development environment for client demos and testing.

**Expected Response Time**: 1-3 business days

**Form URL**: https://forms.gle/D3cB7xY6A44aVusY9

### **Service Account Permissions Issue Identified**
The Firestore service account `service-1075260378031@gcp-sa-firestore.iam.gserviceaccount.com` will need the `cloudkms.cryptoKeyEncrypterDecrypter` role on the KMS key once CMEK is approved.

## 🏗️ **Planned Firestore Configuration**

### **Database Settings**
- **Database ID**: `(default)`
- **Edition**: Standard edition
- **Mode**: Firestore native (not Datastore mode)
- **Location Type**: Region
- **Region**: `southamerica-west1` (Santiago, Chile)
- **Security Rules**: Restrictive (for multi-tenant security)
- **Encryption**: Customer-managed key (pending allowlist approval)

### **Why These Settings?**
- **Region Choice**: Aligns with primary Chilean market and existing GCP architecture
- **Native Mode**: Better for multi-tenant structure with subcollections
- **Restrictive Rules**: Essential for multi-tenant isolation
- **CMEK**: Required by organization security policies

## ✅ **Firebase Auth Emulator Integration Complete**

### **Authentication System Setup (August 4, 2025)**

**Firebase SDK Integration:**
- **Firebase SDK**: Installed in React frontend (`firebase@latest`)
- **Configuration File**: `frontend/src/config/firebase.ts` created
- **Emulator Connection**: Auth emulator (localhost:9099) and Firestore emulator (localhost:8080)
- **Development Mode**: Automatic emulator connection in development environment

**AuthContext Integration:**
- **Updated**: `frontend/src/components/auth/AuthContext.tsx` 
- **Real Firebase Auth**: Replaced mock authentication with Firebase Auth SDK
- **Role Mapping**: Automatic role assignment based on email domains
- **Error Handling**: User-friendly Firebase Auth error messages
- **State Management**: Real-time authentication state with `onAuthStateChanged`

**Demo Users Created:**
- **Client Admin**: `admin@xyz.cl` (password: `demo123`)
- **Client User**: `usuario@xyz.cl` (password: `demo123`)  
- **Bank Admin**: `admin@bancoabc.cl` (password: `demo123`)

**Testing Complete:**
- ✅ Login flow working with Firebase Auth emulator
- ✅ Role-based navigation functional
- ✅ User session persistence across page refreshes
- ✅ Logout functionality operational
- ✅ TypeScript compilation successful

## 🚧 **Blocked/Pending Items**

### **Waiting for Google Approval**
- ❌ **Production Firestore Database**: Blocked until CMEK allowlist approval
- ⚠️ **Real Firestore Integration**: Using emulator for development
- ❌ **Security Rules Deployment**: Dependent on production database creation

### **Error Encountered**
```
ERROR: (gcloud.firestore.databases.create) FAILED_PRECONDITION: 
CMEK usage requires allowlisting for this project. 
Please request access by filling out the form at https://forms.gle/D3cB7xY6A44aVusY9.
```

## 📊 **Next Steps (Post-Approval)**

### **Immediate Actions After Approval**
1. **Create Firestore Database** with CMEK encryption
2. **Grant Service Account Permissions** for KMS key access
3. **Set up Firebase Authentication** with email/password provider
4. **Deploy Multi-tenant Security Rules**
5. **Test Database Connectivity** from backend API

### **Integration Architecture**
```
Frontend (React) → Backend API (FastAPI) → Firestore
                ↓
        Firebase Auth (unified user management)
```

### **Security Rules Strategy**
Multi-tenant pool model with role-based access control:
- Bank admins access their bank's data only
- Client users access their client's data only  
- Users can read/write their own profile
- Organization isolation enforced at database level

## 📁 **Related Files**
- `data-approach.md`: Overall Firestore integration strategy
- `data-structure.md`: Complete database schema design
- `gcp-organization.md`: GCP organization architecture and policies
- `documentation.md`: General project progress tracking

## 🔄 **Status Summary**

**Current Status**: 🚀 **Development Environment Fully Operational - Waiting for Production CMEK Approval**

**Progress**: 85% Complete
- ✅ GCP project setup
- ✅ API enablement  
- ✅ KMS key creation
- ✅ CMEK request submitted
- ✅ Firebase Auth emulator setup
- ✅ Frontend Firebase integration
- ✅ Demo users and authentication flow
- ⏳ Awaiting Google CMEK approval for production
- ❌ Production database creation pending

**Development Ready**: Full development environment operational with emulators
**Production Timeline**: Database setup can proceed immediately once CMEK approval is received (expected 1-3 business days)

**Next Steps**: Backend API development and Firestore data integration can proceed using emulators.