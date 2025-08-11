import { initializeApp } from 'firebase/app';
import { getAuth, connectAuthEmulator } from 'firebase/auth';
import { getFirestore, connectFirestoreEmulator } from 'firebase/firestore';

// Firebase configuration for ccm-dev-pool project
const firebaseConfig = {
  apiKey: "AIzaSyAK4xpjT6beAmybFGZIOIbOqDSLxWyvaYE",
  authDomain: "ccm-dev-pool.firebaseapp.com",
  projectId: "ccm-dev-pool",
  storageBucket: "ccm-dev-pool.firebasestorage.app",
  messagingSenderId: "1075260378031",
  appId: "1:1075260378031:web:3f74fc11df6be8673f7d5a"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Auth
export const auth = getAuth(app);

// Initialize Firestore with CMEK database
export const db = getFirestore(app, 'ccm-development');

// Environment configuration
const USE_EMULATOR = process.env.REACT_APP_USE_EMULATOR === 'true';
const USE_CMEK_DATABASE = process.env.REACT_APP_USE_CMEK_DATABASE === 'true';

console.log('🔧 Firebase Configuration:', {
  useEmulator: USE_EMULATOR,
  useCMEKDatabase: USE_CMEK_DATABASE,
  environment: process.env.NODE_ENV
});

// Connect to emulators in development (only if enabled)
if (process.env.NODE_ENV === 'development' && USE_EMULATOR) {
  console.log('🔧 Connecting to Firebase emulators...');
  
  // Connect to Auth emulator
  try {
    connectAuthEmulator(auth, 'http://127.0.0.1:9099');
    console.log('✅ Connected to Auth emulator');
  } catch (error) {
    console.log('ℹ️ Auth emulator already connected');
  }
  
  // Connect to Firestore emulator  
  try {
    connectFirestoreEmulator(db, '127.0.0.1', 8081);
    console.log('✅ Connected to Firestore emulator');
  } catch (error) {
    console.log('ℹ️ Firestore emulator already connected');
  }
} else if (USE_CMEK_DATABASE) {
  console.log('🔐 Using CMEK-enabled Firestore database: ccm-development');
} else {
  console.log('☁️ Using default Firebase configuration');
}

export default app;