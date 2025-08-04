# Firebase Integration Guide - Client Confirmation Manager

## 📋 **Overview**

This document provides step-by-step instructions for setting up Firebase services for the Client Confirmation Manager (CCM2) application, including both development (emulator) and production environments.

## 🎯 **Prerequisites**

### **System Requirements**
- Node.js 16+ installed
- Java 11+ installed (for Firebase emulators)
- Google Cloud CLI (gcloud) configured
- Git repository with CCM2 codebase

### **GCP Project Setup**
- GCP Project: `ccm-dev-pool` created in Development folder
- Firebase project enabled in GCP project
- Required APIs enabled (Firestore, Firebase Auth, Cloud Functions, etc.)

## 🔧 **Development Environment Setup**

### **Step 1: Install Firebase CLI**
```bash
# Install Firebase CLI globally
npm install -g firebase-tools

# Verify installation
firebase --version
```

### **Step 2: Firebase Project Initialization**
```bash
# Navigate to project directory
cd C:\Users\bencl\Proyectos\ccm2.0

# Login to Firebase
firebase login

# Initialize Firebase project
firebase init
```

**Configuration Options:**
- Select: ✅ Firestore, ✅ Emulators
- Project: Use existing project → `ccm-dev-pool`
- Firestore Rules: `firestore.rules` (default)
- Firestore Indexes: `firestore.indexes.json` (default)
- Emulators: ✅ Authentication Emulator, ✅ Firestore Emulator
- Auth Emulator Port: `9099` (default)
- Firestore Emulator Port: `8080` (default)
- Emulator UI: ✅ Yes, any available port

### **Step 3: Frontend Firebase Integration**

**Create Firebase Configuration:**
```typescript
// frontend/src/config/firebase.ts
import { initializeApp } from 'firebase/app';
import { getAuth, connectAuthEmulator } from 'firebase/auth';
import { getFirestore, connectFirestoreEmulator } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: "demo-api-key",
  authDomain: "ccm-dev-pool.firebaseapp.com",
  projectId: "ccm-dev-pool",
  storageBucket: "ccm-dev-pool.appspot.com",
  messagingSenderId: "1075260378031",
  appId: "demo-app-id"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);

// Connect to emulators in development
if (process.env.NODE_ENV === 'development') {
  try {
    connectAuthEmulator(auth, 'http://127.0.0.1:9099');
    connectFirestoreEmulator(db, '127.0.0.1', 8080);
  } catch (error) {
    console.log('Emulators already connected');
  }
}

export default app;
```

**Install Firebase SDK:**
```bash
cd frontend
npm install firebase
```

**Update Authentication Context:**
```typescript
// frontend/src/components/auth/AuthContext.tsx
import { signInWithEmailAndPassword, signOut, onAuthStateChanged } from 'firebase/auth';
import { auth } from '../../config/firebase';

// Replace mock authentication with Firebase Auth
// See implementation in AuthContext.tsx
```

### **Step 4: Start Development Environment**

**Terminal 1 - Firebase Emulators:**
```bash
firebase emulators:start
```

**Terminal 2 - React Development Server:**
```bash
cd frontend
npm start
```

**Access Points:**
- **Emulator UI**: http://127.0.0.1:4000/
- **Authentication**: http://127.0.0.1:4000/auth
- **Firestore**: http://127.0.0.1:4000/firestore
- **React App**: http://localhost:3000

## 👤 **Demo User Management**

### **Creating Demo Users**
1. Open Firebase Auth Emulator UI: http://127.0.0.1:4000/auth
2. Click **"Add user"**
3. Create these users:

**Client Admin:**
- Email: `admin@xyz.cl`
- Password: `demo123`

**Client User:**
- Email: `usuario@xyz.cl`  
- Password: `demo123`

**Bank Admin:**
- Email: `admin@bancoabc.cl`
- Password: `demo123`

### **Role Assignment Logic**
```typescript
// Automatic role mapping in AuthContext.tsx
const mapFirebaseUserToUser = (firebaseUser: FirebaseUser): User => {
  let role: 'client_user' | 'client_admin' | 'bank_admin';
  
  if (firebaseUser.email?.includes('@bancoabc.cl')) {
    role = 'bank_admin';
  } else if (firebaseUser.email === 'admin@xyz.cl') {
    role = 'client_admin';
  } else {
    role = 'client_user';
  }

  return {
    id: firebaseUser.uid,
    name: firebaseUser.displayName || firebaseUser.email?.split('@')[0] || 'User',
    email: firebaseUser.email || '',
    role
  };
};
```

## 🔐 **Firestore Security Rules**

### **Development Rules (Permissive)**
```javascript
// firestore.rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow read/write access on all documents to authenticated users
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

### **Production Rules (Multi-tenant)**
```javascript
// firestore.rules (Production)
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read their own profile
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Bank admins access their bank's data
    match /banks/{bankId}/{document=**} {
      allow read, write: if request.auth != null && 
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.organizationId == bankId &&
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.organizationType == 'bank';
    }
    
    // Client users access their client's data
    match /clients/{clientId}/{document=**} {
      allow read, write: if request.auth != null && 
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.organizationId == clientId &&
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.organizationType == 'client';
    }
  }
}
```

## 🚀 **Production Deployment**

### **Prerequisites for Production**
- Google CMEK allowlist approval received
- Production Firestore database created with CMEK encryption
- Real domain and SSL certificates configured

### **Production Configuration Updates**

**Firebase Config for Production:**
```typescript
// frontend/src/config/firebase.ts (Production)
const firebaseConfig = {
  apiKey: "your-real-api-key",
  authDomain: "ccm-dev-pool.firebaseapp.com", 
  projectId: "ccm-dev-pool",
  storageBucket: "ccm-dev-pool.appspot.com",
  messagingSenderId: "1075260378031",
  appId: "your-real-app-id"
};

// Remove emulator connections for production
// if (process.env.NODE_ENV === 'development') { ... }
```

**Production User Creation:**
1. Create real users with actual email addresses
2. Set up email verification flows
3. Configure password requirements
4. Implement role assignment through user claims

### **Deployment Commands**
```bash
# Deploy Firestore rules
firebase deploy --only firestore:rules

# Deploy Firestore indexes  
firebase deploy --only firestore:indexes

# Full deployment
firebase deploy
```

## 🧪 **Testing & Validation**

### **Authentication Testing Checklist**
- [ ] Login with all three user types
- [ ] Role-based navigation working
- [ ] Session persistence across page refresh
- [ ] Logout functionality
- [ ] Error handling for invalid credentials
- [ ] Automatic role assignment from email domains

### **Firestore Testing Checklist**  
- [ ] Data reading from Firestore emulator
- [ ] Data writing to Firestore emulator
- [ ] Security rules enforcement
- [ ] Multi-tenant data isolation
- [ ] Error handling for database operations

### **Development Workflow Testing**
- [ ] Hot reloading works with Firebase integration
- [ ] TypeScript compilation without errors
- [ ] Console shows Firebase connection logs
- [ ] Emulator UI displays authentication events
- [ ] Emulator UI shows Firestore data changes

## 🔍 **Troubleshooting**

### **Common Issues**

**Firebase Emulators Won't Start:**
- Ensure Java 11+ is installed and in PATH
- Check ports 4000, 8080, 9099 are not in use
- Restart terminal after Java installation

**Frontend Won't Connect to Emulators:**
- Verify emulator URLs in firebase.ts configuration
- Check browser console for connection errors
- Ensure Firebase SDK is properly installed

**Authentication Not Working:**
- Check if demo users are created in Auth emulator
- Verify email/password combinations
- Check browser network tab for API calls

**TypeScript Compilation Errors:**
- Ensure Firebase SDK types are installed
- Check import statements in firebase.ts
- Verify TypeScript configuration includes Firebase types

### **Debug Commands**
```bash
# Check Firebase CLI version
firebase --version

# Check project configuration
firebase projects:list

# Check emulator status
firebase emulators:exec "echo 'Emulators running'"

# Test Firestore connection
firebase firestore:indexes

# Check authentication setup
firebase auth:export users.json --project ccm-dev-pool
```

## 📈 **Performance Considerations**

### **Development Environment**
- Emulators run locally for fast response times
- No network latency for authentication/database operations
- Instant user creation and data manipulation
- Hot reloading preserved with Firebase integration

### **Production Environment**
- Consider Firebase Auth caching strategies
- Implement proper error boundaries for network failures
- Use Firestore offline persistence for better UX
- Monitor Firebase usage quotas and costs

## 🔒 **Security Best Practices**

### **Development Security**
- Never commit real Firebase API keys to version control
- Use environment variables for configuration
- Keep emulator data separate from production
- Regularly clear emulator data during development

### **Production Security**
- Implement proper Firestore security rules
- Use Firebase Auth custom claims for role management
- Enable audit logging for all database operations
- Regular security rule testing and validation
- Monitor for suspicious authentication patterns

## 📚 **Related Documentation**

- `firestore.md`: Detailed Firestore setup and CMEK configuration
- `data-structure.md`: Complete database schema design
- `data-approach.md`: Overall Firebase integration strategy
- `gcp-organization.md`: GCP organization architecture
- `documentation.md`: Project progress and milestones

This guide provides a complete reference for Firebase integration in the CCM2 project, from development setup through production deployment.