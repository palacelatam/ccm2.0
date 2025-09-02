/**
 * Migration script: WhatsApp to SMS Configuration
 * 
 * This script migrates existing WhatsApp alert configurations to SMS format
 * across all client configuration documents in the database.
 * 
 * Changes:
 * - whatsappConfirmedTrades -> smsConfirmedTrades
 * - whatsappDisputedTrades -> smsDisputedTrades
 * - Preserves existing phone numbers and enabled status
 * - Removes old WhatsApp fields after migration
 */

const admin = require('firebase-admin');

// Initialize Firebase Admin
const serviceAccount = require('../backend/ccm-storage-service-account.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: 'https://ccm-dev-pool.firebaseio.com'
});

// Get CMEK Firestore instance
const db = admin.firestore();
db.settings({
  databaseId: 'ccm-development'
});

async function migrateWhatsAppToSms() {
  console.log('🔄 Starting WhatsApp to SMS migration...');
  
  try {
    // Get all client documents
    const clientsSnapshot = await db.collection('clients').get();
    let migratedCount = 0;
    let errorCount = 0;
    
    console.log(`📋 Found ${clientsSnapshot.size} client(s) to process`);
    
    for (const clientDoc of clientsSnapshot.docs) {
      const clientId = clientDoc.id;
      console.log(`\n🔍 Processing client: ${clientId}`);
      
      try {
        // Get the configuration document
        const configRef = db.collection('clients').doc(clientId).collection('settings').doc('configuration');
        const configDoc = await configRef.get();
        
        if (!configDoc.exists) {
          console.log(`  ⚠️  No configuration document found for client ${clientId}`);
          continue;
        }
        
        const configData = configDoc.data();
        const alerts = configData.alerts || {};
        
        // Check if WhatsApp configuration exists
        const whatsappConfirmed = alerts.whatsappConfirmedTrades;
        const whatsappDisputed = alerts.whatsappDisputedTrades;
        
        if (!whatsappConfirmed && !whatsappDisputed) {
          console.log(`  ✅ No WhatsApp configuration found for client ${clientId} - skipping`);
          continue;
        }
        
        // Prepare the migration data
        const updates = {
          ...alerts
        };
        
        // Migrate whatsappConfirmedTrades to smsConfirmedTrades
        if (whatsappConfirmed) {
          updates.smsConfirmedTrades = {
            enabled: whatsappConfirmed.enabled || false,
            phones: whatsappConfirmed.phones || []
          };
          delete updates.whatsappConfirmedTrades;
          console.log(`  📱 Migrated confirmed trades: enabled=${updates.smsConfirmedTrades.enabled}, phones=${updates.smsConfirmedTrades.phones.length}`);
        }
        
        // Migrate whatsappDisputedTrades to smsDisputedTrades  
        if (whatsappDisputed) {
          updates.smsDisputedTrades = {
            enabled: whatsappDisputed.enabled || false,
            phones: whatsappDisputed.phones || []
          };
          delete updates.whatsappDisputedTrades;
          console.log(`  📱 Migrated disputed trades: enabled=${updates.smsDisputedTrades.enabled}, phones=${updates.smsDisputedTrades.phones.length}`);
        }
        
        // Update the document
        await configRef.update({
          alerts: updates
        });
        
        migratedCount++;
        console.log(`  ✅ Successfully migrated client ${clientId}`);
        
      } catch (error) {
        errorCount++;
        console.error(`  ❌ Error migrating client ${clientId}:`, error.message);
      }
    }
    
    console.log(`\n🎉 Migration completed!`);
    console.log(`✅ Successfully migrated: ${migratedCount} client(s)`);
    console.log(`❌ Errors encountered: ${errorCount} client(s)`);
    
  } catch (error) {
    console.error('💥 Migration failed:', error);
    process.exit(1);
  }
}

// Verification function to check migration results
async function verifyMigration() {
  console.log('\n🔍 Verifying migration results...');
  
  try {
    const clientsSnapshot = await db.collection('clients').get();
    
    for (const clientDoc of clientsSnapshot.docs) {
      const clientId = clientDoc.id;
      
      const configRef = db.collection('clients').doc(clientId).collection('settings').doc('configuration');
      const configDoc = await configRef.get();
      
      if (!configDoc.exists) continue;
      
      const alerts = configDoc.data().alerts || {};
      
      // Check for remaining WhatsApp fields (should be none)
      if (alerts.whatsappConfirmedTrades || alerts.whatsappDisputedTrades) {
        console.log(`⚠️  Client ${clientId} still has WhatsApp fields!`);
      }
      
      // Check for new SMS fields
      if (alerts.smsConfirmedTrades || alerts.smsDisputedTrades) {
        console.log(`✅ Client ${clientId} has SMS configuration`);
        if (alerts.smsConfirmedTrades) {
          console.log(`   📱 Confirmed SMS: enabled=${alerts.smsConfirmedTrades.enabled}, phones=${alerts.smsConfirmedTrades.phones?.length || 0}`);
        }
        if (alerts.smsDisputedTrades) {
          console.log(`   📱 Disputed SMS: enabled=${alerts.smsDisputedTrades.enabled}, phones=${alerts.smsDisputedTrades.phones?.length || 0}`);
        }
      }
    }
    
    console.log('\n✅ Verification completed');
    
  } catch (error) {
    console.error('❌ Verification failed:', error);
  }
}

// Main execution
async function main() {
  console.log('📱 WhatsApp to SMS Migration Script');
  console.log('====================================');
  
  await migrateWhatsAppToSms();
  await verifyMigration();
  
  // Close the connection
  await admin.app().delete();
  console.log('\n🔒 Database connection closed');
}

// Handle script execution
if (require.main === module) {
  main().catch(console.error);
}

module.exports = { migrateWhatsAppToSms, verifyMigration };