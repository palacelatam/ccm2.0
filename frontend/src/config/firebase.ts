import { initializeApp } from 'firebase/app';
import { getAuth, connectAuthEmulator } from 'firebase/auth';
import { getFirestore, connectFirestoreEmulator } from 'firebase/firestore';

// Firebase configuration for ccm-dev-pool project
const firebaseConfig = {
  apiKey: "demo-api-key", // For emulator, this can be a dummy value
  authDomain: "ccm-dev-pool.firebaseapp.com",
  projectId: "ccm-dev-pool",
  storageBucket: "ccm-dev-pool.appspot.com",
  messagingSenderId: "1075260378031",
  appId: "demo-app-id" // For emulator, this can be a dummy value
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Auth
export const auth = getAuth(app);

// Initialize Firestore
export const db = getFirestore(app);

// Connect to emulators in development
if (process.env.NODE_ENV === 'development') {
  // Connect to Auth emulator
  try {
    connectAuthEmulator(auth, 'http://127.0.0.1:9099');
  } catch (error) {
    // Emulator already connected
  }
  
  // Connect to Firestore emulator  
  try {
    connectFirestoreEmulator(db, '127.0.0.1', 8081);
  } catch (error) {
    // Emulator already connected
  }
}

export default app;