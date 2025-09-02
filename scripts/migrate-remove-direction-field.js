const admin = require('firebase-admin');

// Initialize Firebase Admin SDK
if (!admin.apps.length) {
  admin.initializeApp({
    credential: admin.credential.applicationDefault(),
    projectId: 'ccm-firestore'
  });
}

const db = admin.firestore();

async function removeDirectionFieldFromSettlementRules() {
  console.log('🔄 Starting migration to remove direction field from settlement rules...\n');
  
  let totalRulesUpdated = 0;
  let totalClientsProcessed = 0;
  
  try {
    // Get all banks
    const banksSnapshot = await db.collection('banks').get();
    
    for (const bankDoc of banksSnapshot.docs) {
      const bankId = bankDoc.id;
      const bankName = bankDoc.data().name || bankId;
      console.log(`📋 Processing bank: ${bankName} (${bankId})`);
      
      // Get all clients for this bank
      const clientsSnapshot = await db.collection('banks').doc(bankId).collection('clients').get();
      
      for (const clientDoc of clientsSnapshot.docs) {
        const clientId = clientDoc.id;
        const clientName = clientDoc.data().name || clientId;
        console.log(`  👤 Processing client: ${clientName} (${clientId})`);
        totalClientsProcessed++;
        
        // Get all settlement rules for this client
        const rulesSnapshot = await db.collection('banks').doc(bankId)
          .collection('clients').doc(clientId)
          .collection('settlementRules').get();
        
        let clientRulesUpdated = 0;
        
        for (const ruleDoc of rulesSnapshot.docs) {
          const ruleData = ruleDoc.data();
          const ruleId = ruleDoc.id;
          
          // Check if the rule has a direction field
          if ('direction' in ruleData) {
            console.log(`    🔧 Removing direction field from rule: ${ruleData.name || ruleId} (was: ${ruleData.direction})`);
            
            // Create update object without direction field
            const { direction, ...updatedData } = ruleData;
            
            // Update the document
            await db.collection('banks').doc(bankId)
              .collection('clients').doc(clientId)
              .collection('settlementRules').doc(ruleId)
              .set(updatedData);
            
            clientRulesUpdated++;
            totalRulesUpdated++;
          }
        }
        
        console.log(`    ✅ Updated ${clientRulesUpdated} settlement rules for client ${clientName}`);
      }
      
      console.log(`✅ Completed bank: ${bankName}\n`);
    }
    
    console.log('🎉 Migration completed successfully!');
    console.log(`📊 Summary:`);
    console.log(`   - Clients processed: ${totalClientsProcessed}`);
    console.log(`   - Settlement rules updated: ${totalRulesUpdated}`);
    
  } catch (error) {
    console.error('❌ Migration failed:', error);
    throw error;
  }
}

// Run the migration
removeDirectionFieldFromSettlementRules()
  .then(() => {
    console.log('\n✅ Migration script completed');
    process.exit(0);
  })
  .catch((error) => {
    console.error('\n❌ Migration script failed:', error);
    process.exit(1);
  });