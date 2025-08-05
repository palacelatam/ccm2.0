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

async function seedDemoData() {
  console.log('🌱 Starting demo data seeding...');
  
  try {
    // Clear existing data (optional)
    console.log('🧹 Clearing existing demo data...');
    
    // 1. Create Roles
    await seedRoles();
    
    // 2. Create Banks
    await seedBanks();
    
    // 3. Create Clients
    await seedClients();
    
    // 4. Create Users (linking to existing Firebase Auth users)
    await seedUsers();
    
    // 5. Create System Settings
    await seedSystemSettings();
    
    console.log('✅ Demo data seeding completed successfully!');
    console.log('');
    console.log('Demo Data Summary:');
    console.log('- 1 Bank: Banco ABC');
    console.log('- 1 Client: XYZ Corporation');
    console.log('- 3 Users: Bank Admin, Client Admin, Client User');
    console.log('- Settlement rules, bank accounts, and system settings');
    console.log('');
    console.log('🌐 View in Emulator UI: http://127.0.0.1:4000/firestore');
    
  } catch (error) {
    console.error('❌ Error seeding demo data:', error);
  }
}

async function seedRoles() {
  console.log('👥 Creating roles...');
  
  const roles = [
    {
      id: 'bank_admin',
      displayName: 'Bank Administrator',
      description: 'Full administrative access for bank operations',
      permissions: [
        'manage_client_segments',
        'manage_instruction_letters', 
        'view_all_clients',
        'manage_bank_settings',
        'view_analytics'
      ]
    },
    {
      id: 'client_admin', 
      displayName: 'Client Administrator',
      description: 'Administrative access for client organization',
      permissions: [
        'view_dashboard',
        'manage_settings',
        'manage_settlement_rules',
        'manage_bank_accounts',
        'manage_data_mappings',
        'manage_users',
        'view_trades',
        'view_confirmations'
      ]
    },
    {
      id: 'client_user',
      displayName: 'Client User', 
      description: 'Standard user access for viewing trades and confirmations',
      permissions: [
        'view_dashboard',
        'view_trades',
        'view_confirmations'
      ]
    }
  ];
  
  for (const role of roles) {
    await db.collection('roles').doc(role.id).set({
      displayName: role.displayName,
      description: role.description,
      permissions: role.permissions,
      createdAt: new Date(),
      lastUpdatedAt: new Date()
    });
  }
  
  console.log('✅ Roles created');
}

async function seedBanks() {
  console.log('🏛️ Creating banks...');
  
  const bankId = 'banco-abc';
  
  // Create main bank document
  await db.collection('banks').doc(bankId).set({
    name: 'Banco ABC',
    taxId: '96.543.210-K',
    country: 'CL',
    swiftCode: 'ABCCCL22',
    status: 'active',
    createdAt: new Date(),
    lastUpdatedAt: new Date(),
    lastUpdatedBy: db.doc('users/J3oRdcf6VuVKcrbeti9hfDSxSgJR') // Will be updated with real UID
  });
  
  // Create client segments
  const segments = [
    {
      id: 'premium',
      name: 'Premium Clients',
      description: 'High-value corporate clients requiring premium service'
    },
    {
      id: 'standard',
      name: 'Standard Corporate',
      description: 'Standard corporate clients with regular trading volumes'
    },
    {
      id: 'startup',
      name: 'Startup & SME',
      description: 'Small and medium enterprises, startup companies'
    }
  ];
  
  for (const segment of segments) {
    await db.collection('banks').doc(bankId).collection('clientSegments').doc(segment.id).set({
      name: segment.name,
      description: segment.description,
      createdAt: new Date(),
      lastUpdatedAt: new Date(),
      lastUpdatedBy: db.doc('users/J3oRdcf6VuVKcrbeti9hfDSxSgJR')
    });
  }
  
  // Create settlement instruction letters
  const letters = [
    {
      id: 'fx-spot-premium',
      active: true,
      priority: 1,
      ruleName: 'FX Spot - Premium Clients',
      product: 'FX_SPOT',
      clientSegmentId: db.doc(`banks/${bankId}/clientSegments/premium`),
      documentName: 'fx_spot_premium_template.pdf',
      documentUrl: '/templates/fx_spot_premium_template.pdf',
      templateVariables: ['client_name', 'trade_date', 'value_date', 'currency_pair', 'amount', 'rate']
    },
    {
      id: 'fx-forward-standard',
      active: true,
      priority: 2,
      ruleName: 'FX Forward - Standard',
      product: 'FX_FORWARD',
      clientSegmentId: db.doc(`banks/${bankId}/clientSegments/standard`),
      documentName: 'fx_forward_standard_template.pdf',
      documentUrl: '/templates/fx_forward_standard_template.pdf',
      templateVariables: ['client_name', 'trade_date', 'value_date', 'currency_pair', 'amount', 'rate', 'forward_points']
    }
  ];
  
  for (const letter of letters) {
    await db.collection('banks').doc(bankId).collection('settlementInstructionLetters').doc(letter.id).set({
      ...letter,
      createdAt: new Date(),
      lastUpdatedAt: new Date(),
      lastUpdatedBy: db.doc('users/J3oRdcf6VuVKcrbeti9hfDSxSgJR')
    });
  }
  
  // Create bank system settings
  await db.collection('banks').doc(bankId).collection('systemSettings').doc('configuration').set({
    defaultCurrency: 'CLP',
    supportedCurrencies: ['CLP', 'USD', 'EUR', 'GBP', 'JPY', 'BRL', 'ARS'],
    supportedProducts: ['FX_SPOT', 'FX_FORWARD', 'FX_SWAP'],
    lastUpdatedAt: new Date(),
    lastUpdatedBy: db.doc('users/J3oRdcf6VuVKcrbeti9hfDSxSgJR')
  });
  
  console.log('✅ Bank data created');
}

async function seedClients() {
  console.log('🏢 Creating clients...');
  
  const clientId = 'xyz-corp';
  const bankId = 'banco-abc';
  
  // Create main client document
  await db.collection('clients').doc(clientId).set({
    name: 'XYZ Corporation',
    taxId: '76.123.456-7',
    bankId: db.doc(`banks/${bankId}`),
    onboardingDate: new Date('2024-01-15'),
    createdAt: new Date(),
    lastUpdatedAt: new Date(),
    lastUpdatedBy: db.doc('users/XPrg33fON0Tsf7R1s8Up1YNU69cz')
  });
  
  // Create client settings
  await db.collection('clients').doc(clientId).collection('settings').doc('configuration').set({
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
        emails: ['admin@xyz.cl', 'treasury@xyz.cl']
      },
      emailDisputedTrades: {
        enabled: true,
        emails: ['admin@xyz.cl', 'treasury@xyz.cl', 'risk@xyz.cl']
      },
      whatsappConfirmedTrades: {
        enabled: false,
        phones: []
      },
      whatsappDisputedTrades: {
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
    lastUpdatedBy: db.doc('users/XPrg33fON0Tsf7R1s8Up1YNU69cz')
  });
  
  // Clear existing settlement rules first
  const existingRules = await db.collection('clients').doc(clientId).collection('settlementRules').get();
  const batch = db.batch();
  existingRules.docs.forEach(doc => {
    batch.delete(doc.ref);
  });
  await batch.commit();
  console.log(`Cleared ${existingRules.docs.length} existing settlement rules`);

  // Create settlement rules (using auto-generated IDs)
  const settlementRules = [
    {
      active: true,
      priority: 1,
      name: 'USD/CLP Spot Settlements',
      counterparty: 'Banco ABC',
      cashflowCurrency: 'USD',
      direction: 'IN',
      product: 'FX_SPOT',
      bankAccountId: 'usd-account-xyz'
    },
    {
      active: true,
      priority: 2,
      name: 'EUR/CLP Spot Settlements',
      counterparty: 'Banco ABC',
      cashflowCurrency: 'EUR',
      direction: 'IN',
      product: 'FX_SPOT',
      bankAccountId: 'eur-account-xyz'
    },
    {
      active: true,
      priority: 3,
      name: 'CLP Outbound Settlements',
      counterparty: 'Banco ABC',
      cashflowCurrency: 'CLP',
      direction: 'OUT',
      product: 'FX_SPOT',
      bankAccountId: 'clp-account-xyz'
    }
  ];
  
  for (const rule of settlementRules) {
    // Use add() to auto-generate unique IDs
    await db.collection('clients').doc(clientId).collection('settlementRules').add({
      ...rule,
      createdAt: new Date(),
      lastUpdatedAt: new Date(),
      lastUpdatedBy: db.doc('users/XPrg33fON0Tsf7R1s8Up1YNU69cz')
    });
  }
  
  // Create bank accounts
  const bankAccounts = [
    {
      id: 'usd-account-xyz',
      accountName: 'XYZ Corp USD Operating Account',
      bankName: 'Banco ABC',
      swiftCode: 'ABCCCL22',
      accountCurrency: 'USD',
      accountNumber: '2015678901',
      isDefault: false
    },
    {
      id: 'eur-account-xyz',
      accountName: 'XYZ Corp EUR Treasury Account',
      bankName: 'Banco ABC',
      swiftCode: 'ABCCCL22',
      accountCurrency: 'EUR',
      accountNumber: '2017789012',
      isDefault: false
    },
    {
      id: 'clp-account-xyz',
      accountName: 'XYZ Corp CLP Main Account',
      bankName: 'Banco ABC',
      swiftCode: 'ABCCCL22',
      accountCurrency: 'CLP',
      accountNumber: '2011234567',
      isDefault: true
    }
  ];
  
  for (const account of bankAccounts) {
    await db.collection('clients').doc(clientId).collection('bankAccounts').doc(account.id).set({
      ...account,
      createdAt: new Date(),
      lastUpdatedAt: new Date(),
      lastUpdatedBy: db.doc('users/XPrg33fON0Tsf7R1s8Up1YNU69cz')
    });
  }
  
  console.log('✅ Client data created');
}

async function seedUsers() {
  console.log('👤 Creating user profiles...');
  
  // These UIDs should match your Firebase Auth emulator users
  // You'll need to get the actual UIDs from your emulator
  const users = [
    {
      uid: 'J3oRdcf6VuVKcrbeti9hfDSxSgJR', // Replace with actual UID from emulator
      email: 'admin@bancoabc.cl',
      firstName: 'Carlos',
      lastName: 'Rodriguez',
      primaryRole: db.doc('roles/bank_admin'),
      organizationId: db.doc('banks/banco-abc'),
      organizationType: 'bank'
    },
    {
      uid: 'XPrg33fON0Tsf7R1s8Up1YNU69cz', // Replace with actual UID from emulator
      email: 'admin@xyz.cl',
      firstName: 'Maria',
      lastName: 'Gonzalez',
      primaryRole: db.doc('roles/client_admin'),
      organizationId: db.doc('clients/xyz-corp'),
      organizationType: 'client'
    },
    {
      uid: 't1VxX6WUFmzFcEZwhOsFjcVNk3n5', // Replace with actual UID from emulator
      email: 'usuario@xyz.cl',
      firstName: 'Juan',
      lastName: 'Perez',
      primaryRole: db.doc('roles/client_user'),
      organizationId: db.doc('clients/xyz-corp'),
      organizationType: 'client'
    }
  ];
  
  for (const user of users) {
    await db.collection('users').doc(user.uid).set({
      firstName: user.firstName,
      lastName: user.lastName,
      email: user.email,
      roles: [user.primaryRole],
      primaryRole: user.primaryRole,
      organizationId: user.organizationId,
      organizationType: user.organizationType,
      language: 'es',
      timezone: 'America/Santiago',
      loginMetadata: {
        lastLoginAt: new Date(),
        lastLoginIP: '127.0.0.1',
        loginCount: 1
      },
      status: 'active',
      emailVerified: true,
      twoFactorEnabled: false,
      createdAt: new Date(),
      lastUpdatedAt: new Date(),
      lastUpdatedBy: db.doc(`users/${user.uid}`)
    });
  }
  
  console.log('✅ User profiles created');
}

async function seedSystemSettings() {
  console.log('⚙️ Creating system settings...');
  
  await db.collection('systemSettings').doc('configuration').set({
    supportedLanguages: ['es', 'en', 'pt'],
    supportedCurrencies: ['CLP', 'USD', 'EUR', 'GBP', 'JPY', 'BRL', 'ARS', 'MXN'],
    supportedProducts: ['FX_SPOT', 'FX_FORWARD', 'FX_SWAP', 'FX_OPTION'],
    supportedCountries: ['CL', 'US', 'BR', 'AR', 'MX', 'PE', 'CO'],
    systemMaintenance: {
      isUnderMaintenance: false,
      maintenanceMessage: '',
      scheduledMaintenanceAt: null
    },
    defaultSettings: {
      language: 'es',
      currency: 'CLP',
      timezone: 'America/Santiago',
      theme: 'light'
    },
    featureFlags: {
      whatsappNotifications: false,
      advancedAnalytics: true,
      multiCurrencySupport: true,
      realTimeUpdates: true
    },
    lastUpdatedAt: new Date(),
    lastUpdatedBy: db.doc('users/J3oRdcf6VuVKcrbeti9hfDSxSgJR')
  });
  
  console.log('✅ System settings created');
}

// Run the seeding
seedDemoData().then(() => {
  process.exit(0);
}).catch((error) => {
  console.error('Seeding failed:', error);
  process.exit(1);
});