C:\Users\bencl\Proyectos\ccm2.0\scripts>python create-bank-user.py
👤 Bank User Creation Script
============================

⚠️  IMPORTANT PREREQUISITE:
   The user MUST already exist in Firebase Auth before running this script.
   This script only creates the user profile in Firestore, not the Firebase Auth user.

📋 To create a Firebase Auth user:
   1. Go to Firebase Console > Authentication > Users
   2. Click "Add user" and enter email/password
   3. Or use Firebase Admin SDK to create the user programmatically

✅ Once the Firebase Auth user exists, this script will:
   - Verify the user exists in Firebase Auth
   - Create their user profile in Firestore
   - Link them to a bank organization with proper role

🔥 Have you already created the user in Firebase Auth? (y/N): y
CMEK Firestore client initialized successfully
? User Email (e.g., admin@bci.cl): admin@bci.cl
❌ Error creating bank user: The default Firebase app does not exist. Make sure to initialize the SDK by calling initialize_app().

💡 Tips:
- Make sure the user exists in Firebase Auth first
- Verify the bank exists (create with create-bank.py if needed)
- Check that you have proper Firebase Admin permissions