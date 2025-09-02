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

async function seedAdditionalClients() {
  console.log('🌱 Seeding additional demo clients...');
  
  try {
    const bankId = 'banco-abc';
    
    // Create additional demo clients that match our assignment IDs
    const additionalClients = [
      {
        id: 'client-1',
        name: 'TechStart Solutions',
        taxId: '77.234.567-8',
        type: 'SME'
      },
      {
        id: 'client-2', 
        name: 'InnovateLab Inc.',
        taxId: '78.345.678-9',
        type: 'Startup'
      },
      {
        id: 'client-3',
        name: 'Global Finance Corp',
        taxId: '79.456.789-0',
        type: 'Corporate'
      },
      {
        id: 'client-4',
        name: 'Startup Dynamics',
        taxId: '80.567.890-1', 
        type: 'Startup'
      },
      {
        id: 'client-5',
        name: 'Regional Enterprises',
        taxId: '81.678.901-2',
        type: 'Corporate'
      }
    ];
    
    for (const client of additionalClients) {
      console.log(`Creating client: ${client.id} - ${client.name}`);
      
      await db.collection('clients').doc(client.id).set({
        name: client.name,
        taxId: client.taxId,
        bankId: db.doc(`banks/${bankId}`),
        clientType: client.type,
        onboardingDate: new Date('2024-01-15'),
        status: 'active',
        createdAt: new Date(),
        lastUpdatedAt: new Date(),
        lastUpdatedBy: db.doc('users/J3oRdcf6VuVKcrbeti9hfDSxSgJR')
      });
      
      // Create basic client settings for each client
      await db.collection('clients').doc(client.id).collection('settings').doc('configuration').set({
        automation: {
          dataSharing: true,
          autoConfirmMatched: {
            enabled: true,
            delayMinutes: 15
          },
          autoCartaInstruccion: true,
          autoConfirmDisputed: {
            enabled: false,
            delayMinutes: 60
          }
        },
        alerts: {
          emailConfirmedTrades: {
            enabled: true,
            emails: [`admin@${client.id}.cl`]
          },
          emailDisputedTrades: {
            enabled: true,
            emails: [`admin@${client.id}.cl`, `risk@${client.id}.cl`]
          },
          smsConfirmedTrades: {
            enabled: false,
            phones: []
          },
          smsDisputedTrades: {
            enabled: false,
            phones: []
          }
        },
        display: {
          theme: 'light',
          currency: 'CLP',
          timezone: 'America/Santiago',
          language: 'es'
        },
        lastUpdatedAt: new Date(),
        lastUpdatedBy: db.doc('users/J3oRdcf6VuVKcrbeti9hfDSxSgJR')
      });
    }
    
    console.log('✅ Additional demo clients created successfully!');
    
    // Verify the clients were created
    const clientsSnapshot = await db.collection('clients').get();
    console.log(`\n📊 Total clients in database: ${clientsSnapshot.size}`);
    clientsSnapshot.forEach(doc => {
      const data = doc.data();
      console.log(`- ${doc.id}: ${data.name}`);
    });
    
  } catch (error) {
    console.error('❌ Error seeding additional clients:', error);
  }
}

// Run the seeding
seedAdditionalClients().then(() => {
  process.exit(0);
}).catch((error) => {
  console.error('Seeding failed:', error);
  process.exit(1);
});