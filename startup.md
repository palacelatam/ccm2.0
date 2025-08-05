   Step 1: Clean up first

  cd C:\Users\bencl\Proyectos\ccm2.0\scripts
  cleanup.bat

🔥 Step 2: Start Firebase Emulators (SECOND - Required for 
  backend)

  cd C:\Users\bencl\Proyectos\ccm2.0
  firebase emulators:start --import=./demo-data --export-on-exit=./demo-data

  Wait for this message: ✔ All emulators ready! It is now safe      
   to connect your app.

  The emulators will run on:
  - Auth: http://127.0.0.1:9099
  - Firestore: http://127.0.0.1:8081
  - UI: http://127.0.0.1:4000

  🌱 Step 3: Seed Demo Data (THIRD - Optional but recommended)     

  Open a new terminal and run:
  cd C:\Users\bencl\Proyectos\ccm2.0\scripts
  node seed-demo-data.js

  This will populate Firestore with the demo data structure.        

  🐍 Step 4: Start Backend API (FOURTH - Needs emulators 
  running)

  Open a new terminal and run:
  cd C:\Users\bencl\Proyectos\ccm2.0\backend
  start-dev.bat

  Backend will run on: http://127.0.0.1:8000

  ⚛️ Step 5: Start Frontend (LAST - Needs backend running)

  Open a new terminal and run:
  cd C:\Users\bencl\Proyectos\ccm2.0\frontend
  npm start

  Frontend will run on: http://localhost:3000

  ---
  Demo Login Credentials:
  - admin@xyz.cl / demo123
  - usuario@xyz.cl / demo123
  - admin@bancoabc.cl / demo123