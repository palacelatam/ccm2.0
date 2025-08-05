const fs = require('fs');
const path = require('path');

// Read the exported auth data to get real UIDs
function getAuthUIDs() {
  console.log('🔍 Reading Firebase Auth UIDs from demo-data...');
  
  try {
    const authDataPath = path.join(__dirname, '..', 'demo-data', 'auth_export', 'accounts.json');
    
    if (!fs.existsSync(authDataPath)) {
      console.error('❌ Auth export data not found at:', authDataPath);
      console.log('💡 Make sure Firebase emulators are running and you have exported demo data');
      return;
    }
    
    const authData = JSON.parse(fs.readFileSync(authDataPath, 'utf8'));
    
    console.log('📋 Firebase Auth UIDs:');
    console.log('');
    
    const uidMap = {};
    
    authData.users.forEach(user => {
      const email = user.email;
      const uid = user.localId;
      const displayName = user.displayName || email.split('@')[0];
      
      console.log(`${displayName}:`);
      console.log(`  Email: ${email}`);
      console.log(`  UID: ${uid}`);
      console.log('');
      
      // Create mapping for easy reference
      if (email.includes('@bancoabc.cl')) {
        uidMap.bankAdmin = uid;
      } else if (email === 'admin@xyz.cl') {
        uidMap.clientAdmin = uid;
      } else if (email === 'usuario@xyz.cl') {
        uidMap.clientUser = uid;
      }
    });
    
    // Update the seeding script with real UIDs
    updateSeedingScript(uidMap);
    
  } catch (error) {
    console.error('❌ Error reading auth data:', error.message);
  }
}

function updateSeedingScript(uidMap) {
  console.log('🔄 Updating seeding script with real UIDs...');
  
  const seedScriptPath = path.join(__dirname, 'seed-demo-data.js');
  let seedScript = fs.readFileSync(seedScriptPath, 'utf8');
  
  // Replace placeholder UIDs with real ones
  if (uidMap.bankAdmin) {
    seedScript = seedScript.replace(/bank-admin-uid/g, uidMap.bankAdmin);
  }
  if (uidMap.clientAdmin) {
    seedScript = seedScript.replace(/client-admin-uid/g, uidMap.clientAdmin);
  }
  if (uidMap.clientUser) {
    seedScript = seedScript.replace(/client-user-uid/g, uidMap.clientUser);
  }
  
  fs.writeFileSync(seedScriptPath, seedScript);
  
  console.log('✅ Seeding script updated with real Firebase Auth UIDs');
  console.log('');
  console.log('🚀 Ready to seed! Run: npm run seed');
}

// Run the UID extraction
getAuthUIDs();