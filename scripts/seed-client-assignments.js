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

async function seedClientAssignments() {
  console.log('🌱 Seeding client segment assignments...');
  
  try {
    const bankId = 'banco-abc';
    
    // Create some demo client assignments for testing
    // We'll create assignments for both real clients and mock client IDs
    const assignments = {
      premium: ['xyz-corp', 'client-3'],  // Mix real and mock clients
      standard: ['client-1', 'client-5'], 
      startup: ['client-2', 'client-4']
    };
    
    console.log('Creating client segment assignments:', assignments);
    
    // Create the assignments document
    await db.collection('banks').doc(bankId).collection('clientSegmentAssignments').doc('assignments').set({
      assignments: assignments,
      lastUpdatedAt: new Date(),
      lastUpdatedBy: db.doc('users/J3oRdcf6VuVKcrbeti9hfDSxSgJR') // Bank admin UID
    });
    
    console.log('✅ Client segment assignments created successfully!');
    
    // Verify the data was created
    const assignmentsDoc = await db.collection('banks').doc(bankId).collection('clientSegmentAssignments').doc('assignments').get();
    if (assignmentsDoc.exists) {
      console.log('✅ Verification - assignments document:', assignmentsDoc.data());
    }
    
  } catch (error) {
    console.error('❌ Error seeding client assignments:', error);
  }
}

// Run the seeding
seedClientAssignments().then(() => {
  process.exit(0);
}).catch((error) => {
  console.error('Seeding failed:', error);
  process.exit(1);
});