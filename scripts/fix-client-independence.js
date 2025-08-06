const { initializeApp } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');

// Initialize Firebase Admin (for emulator)
const app = initializeApp({
  projectId: 'ccm-dev-pool'
});

// Connect to Firestore emulator
const db = getFirestore();
db.settings({
  host: 'localhost:8081',
  ssl: false
});

async function fixClientIndependence() {
  console.log('🔧 Fixing client independence - removing bankId fields...');
  
  try {
    // Get all clients
    const clientsSnapshot = await db.collection('clients').get();
    console.log(`Found ${clientsSnapshot.size} clients to update`);
    
    const batch = db.batch();
    
    clientsSnapshot.forEach(doc => {
      const data = doc.data();
      console.log(`- Updating client ${doc.id}: ${data.name}`);
      
      // Create updated data without bankId
      const updatedData = { ...data };
      delete updatedData.bankId; // Remove bankId field
      
      batch.set(doc.ref, updatedData);
    });
    
    await batch.commit();
    console.log('✅ Successfully removed bankId from all clients');
    
    // Verify the changes
    console.log('\n🔍 Verifying clients are now independent:');
    const updatedClientsSnapshot = await db.collection('clients').get();
    updatedClientsSnapshot.forEach(doc => {
      const data = doc.data();
      const hasBankId = 'bankId' in data;
      console.log(`- ${doc.id}: ${data.name} - bankId present: ${hasBankId}`);
    });
    
  } catch (error) {
    console.error('❌ Error fixing client independence:', error);
  }
}

// Run the fix
fixClientIndependence().then(() => {
  process.exit(0);
}).catch((error) => {
  console.error('Fix failed:', error);
  process.exit(1);
});