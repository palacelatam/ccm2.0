const { initializeApp } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');

// Initialize Firebase Admin for CMEK-enabled database
const app = initializeApp({
  projectId: 'ccm-dev-pool'
});

// Connect to CMEK Firestore database
const db = getFirestore(app, 'ccm-development');

async function seedCMEKDatabase() {
  console.log('🌱 Starting CMEK database seeding...');
  console.log('📍 Database: ccm-development (CMEK-encrypted)');
  console.log('🏗️  Project: ccm-dev-pool');
  
  try {
    // 1. Create Roles
    await seedRoles();
    
    // 2. Create Banks
    await seedBanks();
    
    // 3. Create Clients
    await seedClients();
    
    // 4. Create Users (using placeholder UIDs for now)
    await seedUsers();
    
    // 5. Create System Settings
    await seedSystemSettings();
    
    // 6. Create Client Dashboard Collections (NEW!)
    await seedClientDashboardData();
    
    console.log('✅ CMEK database seeding completed successfully!');
    console.log('');
    console.log('🎯 Database Summary:');
    console.log('- 🏛️  1 Bank: Banco ABC');
    console.log('- 🏢 1 Client: XYZ Corporation');
    console.log('- 👥 3 Users: Bank Admin, Client Admin, Client User');
    console.log('- 📊 Client Dashboard: Unmatched Trades, Matched Trades, Email Matches');
    console.log('- ⚙️  Settlement rules, bank accounts, and system settings');
    console.log('- 🔐 All data encrypted with CMEK');
    console.log('');
    console.log('🌐 View in Firebase Console: https://console.firebase.google.com/project/ccm-dev-pool/firestore');
    
  } catch (error) {
    console.error('❌ Error seeding CMEK database:', error);
    throw error;
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
        'view_confirmations',
        'upload_trades',
        'process_emails'
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
    lastUpdatedBy: db.doc('users/bank-admin-uid') // Will be updated with real UID
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
      lastUpdatedBy: db.doc('users/bank-admin-uid')
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
      lastUpdatedBy: db.doc('users/bank-admin-uid')
    });
  }
  
  // Create bank system settings
  await db.collection('banks').doc(bankId).collection('systemSettings').doc('configuration').set({
    defaultCurrency: 'CLP',
    supportedCurrencies: ['CLP', 'USD', 'EUR', 'GBP', 'JPY', 'BRL', 'ARS'],
    supportedProducts: ['FX_SPOT', 'FX_FORWARD', 'FX_SWAP'],
    lastUpdatedAt: new Date(),
    lastUpdatedBy: db.doc('users/bank-admin-uid')
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
    lastUpdatedBy: db.doc('users/client-admin-uid')
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
    lastUpdatedBy: db.doc('users/client-admin-uid')
  });
  
  // Create settlement rules
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
    await db.collection('clients').doc(clientId).collection('settlementRules').add({
      ...rule,
      createdAt: new Date(),
      lastUpdatedAt: new Date(),
      lastUpdatedBy: db.doc('users/client-admin-uid')
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
      lastUpdatedBy: db.doc('users/client-admin-uid')
    });
  }
  
  console.log('✅ Client data created');
}

async function seedUsers() {
  console.log('👤 Creating user profiles...');
  
  // Using placeholder UIDs - these will be replaced when real Firebase Auth users are created
  const users = [
    {
      uid: 'bank-admin-uid',
      email: 'admin@bancoabc.cl',
      firstName: 'Carlos',
      lastName: 'Rodriguez',
      primaryRole: db.doc('roles/bank_admin'),
      organizationId: db.doc('banks/banco-abc'),
      organizationType: 'bank'
    },
    {
      uid: 'client-admin-uid',
      email: 'admin@xyz.cl',
      firstName: 'Maria',
      lastName: 'Gonzalez',
      primaryRole: db.doc('roles/client_admin'),
      organizationId: db.doc('clients/xyz-corp'),
      organizationType: 'client'
    },
    {
      uid: 'client-user-uid',
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
      realTimeUpdates: true,
      clientDashboard: true
    },
    lastUpdatedAt: new Date(),
    lastUpdatedBy: db.doc('users/bank-admin-uid')
  });
  
  console.log('✅ System settings created');
}

async function seedClientDashboardData() {
  console.log('📊 Creating client dashboard collections...');
  
  const clientId = 'xyz-corp';
  
  // 1. Create Unmatched Trades collection with sample data
  console.log('📋 Creating unmatched trades...');
  
  const unmatchedTrades = [
    {
      TradeNumber: "32010",
      CounterpartyName: "Bci",
      ProductType: "Forward",
      TradeDate: "01-10-2025",
      ValueDate: "01-10-2025",
      Direction: "Buy",
      Currency1: "USD",
      QuantityCurrency1: 330000.0,
      Price: 932.33,
      Currency2: "CLP",
      MaturityDate: "01-10-2026",
      FixingReference: "USD Obs",
      SettlementType: "Compensación",
      SettlementCurrency: "CLP",
      PaymentDate: "03-10-2026",
      CounterpartyPaymentMethod: "SWIFT",
      OurPaymentMethod: "SWIFT",
      status: "unmatched",
      uploadedAt: new Date(),
      uploadedBy: db.doc('users/client-admin-uid')
    },
    {
      TradeNumber: "32011",
      CounterpartyName: "Banco Estado",
      ProductType: "Spot",
      TradeDate: "02-10-2025",
      ValueDate: "04-10-2025",
      Direction: "Sell",
      Currency1: "EUR",
      QuantityCurrency1: 500000.0,
      Price: 1015.75,
      Currency2: "CLP",
      MaturityDate: "04-10-2025",
      FixingReference: "EUR Obs",
      SettlementType: "Compensación",
      SettlementCurrency: "EUR",
      PaymentDate: "04-10-2025",
      CounterpartyPaymentMethod: "LBTR",
      OurPaymentMethod: "LBTR",
      status: "unmatched",
      uploadedAt: new Date(),
      uploadedBy: db.doc('users/client-admin-uid')
    }
  ];
  
  for (const trade of unmatchedTrades) {
    await db.collection('clients').doc(clientId).collection('unmatchedTrades').doc(trade.TradeNumber).set(trade);
  }
  
  // 2. Create Matched Trades collection with sample data
  console.log('✅ Creating matched trades...');
  
  const matchedTrades = [
    {
      TradeNumber: "32013",
      CounterpartyName: "Banco ABC",
      ProductType: "Forward",
      TradeDate: "29-09-2025",
      ValueDate: "01-10-2025",
      Direction: "Buy",
      Currency1: "USD",
      QuantityCurrency1: 1000000.0,
      Price: 932.88,
      Currency2: "CLP",
      MaturityDate: "30-10-2025",
      FixingReference: "USD Obs",
      SettlementType: "Compensación",
      SettlementCurrency: "CLP",
      PaymentDate: "01-11-2025",
      CounterpartyPaymentMethod: "LBTR",
      OurPaymentMethod: "LBTR",
      identified_at: "2025-08-08T16:14:37.216324+00:00",
      match_id: "608d18e1-98cf-4230-b8a0-e20a5c1f153e",
      match_confidence: "89%",
      match_reasons: ["Trade number match", "Amount match", "Currency match"],
      status: "confirmed",
      matchedAt: new Date('2025-08-08T16:14:37.216Z'),
      matchedBy: db.doc('users/client-admin-uid')
    }
  ];
  
  for (const trade of matchedTrades) {
    await db.collection('clients').doc(clientId).collection('matchedTrades').doc(trade.TradeNumber).set(trade);
  }
  
  // 3. Create Email Matches collection with sample data
  console.log('📧 Creating email matches...');
  
  const emailMatches = [
    {
      EmailSender: "confirmacionesderivados@bancoabc.cl",
      EmailDate: "2025-04-04",
      EmailTime: "11:39:04",
      EmailSubject: "Confirmación operación 9239834",
      BankTradeNumber: "9239834",
      match_id: "608d18e1-98cf-4230-b8a0-e20a5c1f153e",
      CounterpartyID: "",
      CounterpartyName: "Banco ABC",
      ProductType: "Forward",
      Direction: "Buy",
      Trader: null,
      Currency1: "USD",
      QuantityCurrency1: 1000000.0,
      Currency2: "CLP",
      SettlementType: "Compensación",
      SettlementCurrency: "CLP",
      TradeDate: "29-09-2025",
      ValueDate: "01-10-2025",
      MaturityDate: "30-10-2025",
      PaymentDate: "01-11-2025",
      Duration: 0,
      Price: 932.98,
      FixingReference: "USD Obs",
      CounterpartyPaymentMethod: "SWIFT",
      OurPaymentMethod: "SWIFT",
      EmailBody: "Estimados señores,\\nSe ha negociado entre Banco ABC y Empresas ABC Limitada la siguiente operación...",
      previous_status: "",
      status: "",
      processedAt: new Date('2025-04-04T11:39:04.000Z'),
      processedBy: db.doc('users/client-admin-uid'),
      llmConfidence: 0.92,
      llmExtractedFields: {
        tradeNumber: "9239834",
        amount: 1000000.0,
        currency: "USD",
        counterparty: "Banco ABC",
        productType: "Forward"
      }
    }
  ];
  
  for (let i = 0; i < emailMatches.length; i++) {
    const email = emailMatches[i];
    await db.collection('clients').doc(clientId).collection('emailMatches').doc(`email-${i + 1}`).set(email);
  }
  
  // 4. Create Dashboard Metadata
  console.log('📊 Creating dashboard metadata...');
  
  await db.collection('clients').doc(clientId).collection('dashboardMetadata').doc('statistics').set({
    totalUnmatchedTrades: unmatchedTrades.length,
    totalMatchedTrades: matchedTrades.length,
    totalEmailMatches: emailMatches.length,
    lastDataUpload: new Date(),
    lastEmailProcessed: new Date('2025-04-04T11:39:04.000Z'),
    matchingAlgorithmVersion: "v2.0",
    llmModelVersion: "claude-3-sonnet-20240229",
    averageMatchConfidence: "89%",
    lastUpdatedAt: new Date(),
    lastUpdatedBy: db.doc('users/client-admin-uid')
  });
  
  console.log('✅ Client dashboard collections created');
}

// Run the seeding
seedCMEKDatabase().then(() => {
  console.log('🎉 CMEK database setup completed successfully!');
  process.exit(0);
}).catch((error) => {
  console.error('❌ CMEK database seeding failed:', error);
  process.exit(1);
});