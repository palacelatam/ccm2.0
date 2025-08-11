# Database Configuration Guide

This guide explains how to switch between Firebase emulators and the CMEK-enabled Firestore database for development.

## 🔐 CMEK Database (Default)

**Active by default** - Your application is now configured to use the persistent, CMEK-encrypted Firestore database.

### Configuration Details
- **Project**: `ccm-dev-pool`
- **Database**: `ccm-development` (CMEK-encrypted)
- **Location**: `southamerica-west1` (Santiago, Chile)
- **Encryption**: Customer-Managed Encryption Keys
- **Persistence**: Data persists between development sessions

### Benefits
- ✅ **Persistent Data**: No data loss when restarting development
- ✅ **Production-like Security**: CMEK encryption matches production setup
- ✅ **Real Database Testing**: Test against actual Firestore features
- ✅ **Client Dashboard Ready**: Pre-populated with v1.0 data structures

### Collections Available
- `roles` (3 user permission levels)
- `banks` (1 bank with subcollections)
- `clients` (1 client with subcollections)
- `users` (3 user profiles)
- `systemSettings` (global configuration)
- **Client Dashboard Collections**:
  - `unmatchedTrades` (2 sample trades)
  - `matchedTrades` (1 matched trade)
  - `emailMatches` (1 processed email)
  - `dashboardMetadata` (statistics)

## 🔧 Firebase Emulators (Optional)

Use emulators for rapid prototyping or when you need to test with clean data frequently.

### Switch to Emulators
```bash
# Windows
switch-to-emulator.bat

# Manual (any OS)
cp frontend/.env.emulator frontend/.env.local
cp backend/.env.emulator backend/.env
```

### Start Emulators
```bash
firebase emulators:start --import=./demo-data --export-on-exit=./demo-data
```

### Benefits
- ✅ **Fast Iteration**: Quick data reset and testing
- ✅ **Offline Development**: No internet connection needed
- ✅ **Safe Experimentation**: Isolated from production data

## ⚡ Quick Switch Commands

### Switch to CMEK Database
```bash
# Windows
switch-to-cmek.bat

# Manual (any OS)  
cp frontend/.env.development frontend/.env.local
cp backend/.env.development backend/.env
```

### Switch to Emulators
```bash
# Windows
switch-to-emulator.bat

# Manual (any OS)
cp frontend/.env.emulator frontend/.env.local
cp backend/.env.emulator backend/.env
```

## 🚀 Starting Your Applications

After switching configurations:

### Frontend
```bash
cd frontend
npm start
```

### Backend
```bash
cd backend
python -m uvicorn main:app --reload
```

## 🔍 Verification

Check your browser console for configuration logs:

**CMEK Mode:**
```
🔧 Firebase Configuration: { useEmulator: false, useCMEKDatabase: true }
🔐 Using CMEK-enabled Firestore database: ccm-development
```

**Emulator Mode:**
```
🔧 Firebase Configuration: { useEmulator: true, useCMEKDatabase: false }
🔧 Connecting to Firebase emulators...
✅ Connected to Firestore emulator
```

## 📊 Viewing Your Data

### CMEK Database
- **Firebase Console**: https://console.firebase.google.com/project/ccm-dev-pool/firestore
- Select database: `ccm-development`

### Emulators
- **Emulator UI**: http://localhost:4000/firestore
- **Direct Firestore**: http://localhost:4000/firestore

## 🔒 Security Notes

- CMEK database uses Google Cloud authentication (gcloud auth application-default login)
- Emulators use no authentication (development only)
- Never commit real credentials to version control
- Environment files (.env.local, .env) are git-ignored for security

## 🛠️ Troubleshooting

### Authentication Issues with CMEK
```bash
gcloud auth application-default login
gcloud config set project ccm-dev-pool
```

### Emulator Connection Issues
1. Ensure emulators are running: `firebase emulators:start`
2. Check ports are available: 8081 (Firestore), 9099 (Auth), 4000 (UI)
3. Clear browser cache if switching configurations

### Configuration Not Applied
1. Restart your development servers
2. Clear browser cache
3. Check console for configuration logs
4. Verify .env.local and .env files were created correctly