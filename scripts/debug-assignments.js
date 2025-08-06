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

async function debugAssignments() {
  console.log('🔍 Debugging client segment assignments...');
  
  try {
    const bankId = 'banco-abc';
    
    // 1. Check if bank exists
    const bankDoc = await db.collection('banks').doc(bankId).get();
    console.log('🏛️ Bank exists:', bankDoc.exists);
    if (bankDoc.exists) {
      console.log('Bank data:', bankDoc.data());
    }
    
    // 2. Check client segments
    console.log('\n📊 Client Segments:');
    const segmentsSnapshot = await db.collection('banks').doc(bankId).collection('clientSegments').get();
    segmentsSnapshot.forEach(doc => {
      console.log(`- ${doc.id}:`, doc.data());
    });
    
    // 3. Check for any client segment assignments (subcollection)
    console.log('\n👥 Client Assignments (subcollection):');
    const assignmentsSnapshot = await db.collection('banks').doc(bankId).collection('clientSegmentAssignments').get();
    console.log('Assignment docs found:', assignmentsSnapshot.size);
    assignmentsSnapshot.forEach(doc => {
      console.log(`- ${doc.id}:`, doc.data());
    });
    
    // 4. Check if assignments are stored as a single document with arrays
    console.log('\n🗂️ Checking for assignments document:');
    const assignmentsDoc = await db.collection('banks').doc(bankId).collection('clientSegmentAssignments').doc('assignments').get();
    if (assignmentsDoc.exists) {
      console.log('Assignments document data:', assignmentsDoc.data());
    } else {
      console.log('No assignments document found');
    }
    
    // 5. Check clients collection to see what client IDs exist
    console.log('\n🏢 Available Clients:');
    const clientsSnapshot = await db.collection('clients').get();
    clientsSnapshot.forEach(doc => {
      const data = doc.data();
      console.log(`- Client ID: ${doc.id}, Name: ${data.name}`);
    });
    
    // 6. Check if there are any other collections that might contain assignments
    console.log('\n🔍 All subcollections under bank:');
    const collections = await db.collection('banks').doc(bankId).listCollections();
    collections.forEach(collection => {
      console.log(`- ${collection.id}`);
    });
    
  } catch (error) {
    console.error('❌ Error debugging assignments:', error);
  }
}

// Run the debug
debugAssignments().then(() => {
  process.exit(0);
}).catch((error) => {
  console.error('Debug failed:', error);
  process.exit(1);
});