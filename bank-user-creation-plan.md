# Bank and User Creation Scripts - Implementation Plan

## Overview

This document outlines the approach for creating modular scripts to manage banks and users in the CCM system. Instead of having monolithic seed scripts, we'll create focused, reusable scripts for each entity type.

## Current System Analysis

### Existing Structure
- **Main seed script**: `scripts/seed-demo-data.js` - Creates everything at once
- **Current banks**: Banco ABC (`banco-abc`) only
- **Current users**: 3 users (1 bank admin, 2 client users)
- **Auth integration**: ✅ **CONFIRMED: Production Firebase Auth with CMEK database (`ccm-development`)**
- **No emulator**: Firebase emulator setup exists but not currently used

### Data Dependencies
```
Banks → Client Segments → Settlement Instruction Letters
  ↓
Bank Admin Users (reference bank documents)
  ↓
Clients → Settlement Rules → Bank Accounts
  ↓  
Client Users (reference client documents)
```

## Proposed Modular Script Architecture

### 1. Bank Management Scripts

#### `scripts/create-bank.js`
**Purpose**: Create individual banks with all required subcollections

**Parameters** (Interactive CLI will ask for these):
```javascript
{
  bankId: "banco-bci",           // Unique bank identifier
  name: "BCI",                  // Display name
  taxId: "97.004.000-5",        // Chilean RUT
  swiftCode: "BCHCCLRM",        // SWIFT/BIC code
  country: "CL"                 // ISO country code
}
```

**System Settings** (Applied as defaults):
```javascript
{
  defaultCurrency: 'CLP',
  supportedCurrencies: ['CLP', 'USD', 'EUR', 'GBP', 'JPY', 'BRL', 'ARS'],
  supportedProducts: ['Spot', 'Forward']
}
```

**Structure**:
- Create main bank document in `/banks/{bankId}`
- ~~Create client segments subcollection~~ (Removed per BC feedback)
- ~~Create settlement instruction letters subcollection~~ (Removed per BC feedback)
- Create bank system settings subcollection (with defaults only)

#### `scripts/create-bank-user.js`
**Purpose**: Create bank admin users

**Parameters** (Interactive CLI will ask for these):
```javascript
{
  email: "admin@bci.cl",        // Must exist in Firebase Auth
  firstName: "Maria",           // User's first name
  lastName: "Silva",            // User's last name
  bankId: "banco-bci",          // Bank they administer
  role: "bank_admin"            // User role
}
```

**Available Roles**:
- `bank_admin` - Full administrative access for bank operations
- `client_admin` - Administrative access for client organization  
- `client_user` - Standard user access for viewing trades and confirmations

**Structure**:
- Get Firebase Auth UID for email (from production Firebase Auth)
- Create user profile in `/users/{uid}`
- Link to bank organization
- Set role-appropriate permissions

### 2. Client Management Scripts

#### `scripts/create-client.js`
**Purpose**: Create individual clients with all required subcollections

**Parameters** (Interactive CLI will ask for these):
```javascript
{
  clientId: "acme-corp",        // Unique client identifier
  name: "ACME Corporation",     // Company name
  taxId: "76.456.789-0",       // Chilean RUT
  bankId: "banco-bci",         // Associated bank
  onboardingDate: "2024-01-15" // When client was onboarded
}
```

**Default Settings** (Applied automatically):
```javascript
{
  automation: {
    dataSharing: true,
    autoConfirmMatched: { enabled: true, delayMinutes: 0 },
    autoCartaInstruccion: false,
    autoConfirmDisputed: { enabled: false, delayMinutes: 0 }
  },
  alerts: {
    emailConfirmedTrades: { enabled: true, emails: [] },
    emailDisputedTrades: { enabled: true, emails: [] }
  },
  display: { theme: 'light', currency: 'CLP', timezone: 'America/Santiago', language: 'es' }
}
```

**Structure**:
- Create main client document in `/clients/{clientId}`
- Create settings subcollection (automation, alerts, display) with defaults
- ~~Create settlement rules subcollection~~ (Removed per BC feedback)
- ~~Create bank accounts subcollection~~ (Removed per BC feedback)

#### `scripts/create-client-user.js`
**Purpose**: Create client users (admin or standard)

**Parameters**:
```javascript
{
  email: "admin@acme.cl",       // Must exist in Firebase Auth
  firstName: "Juan",            // User's first name
  lastName: "Pérez",           // User's last name
  clientId: "acme-corp",       // Client they belong to
  role: "client_admin"         // client_admin or client_user
}
```

**Structure**:
- Get Firebase Auth UID for email
- Create user profile in `/users/{uid}`
- Link to client organization  
- Set role-appropriate permissions

## Real Bank Data Research

### BCI Bank Details
```javascript
{
  bankId: "banco-bci",
  name: "BCI",
  taxId: "97.004.000-5",        // Real BCI RUT
  swiftCode: "BCHCCLRM",        // Real BCI SWIFT code
  country: "CL",
  fullName: "Banco de Credito e Inversiones"
}
```

### Itaú Bank Details  
```javascript
{
  bankId: "banco-itau",
  name: "Banco Itaú Chile",
  taxId: "97.023.000-9",        // Real Itaú RUT
  swiftCode: "ITAYCLRM",        // Real Itaú SWIFT code  
  country: "CL",
  fullName: "Banco Itaú Chile"
}
```

## Script Implementation Details

### Base Configuration Template

#### Bank Templates
```javascript
// Default system settings for banks (only thing created)
const DEFAULT_BANK_SETTINGS = {
  defaultCurrency: 'CLP',
  supportedCurrencies: ['CLP', 'USD', 'EUR', 'GBP', 'JPY', 'BRL', 'ARS'],
  supportedProducts: ['Spot', 'Forward']
};
```

#### Client Templates
```javascript
// Default automation settings for clients
const DEFAULT_CLIENT_SETTINGS = {
  automation: {
    dataSharing: true,
    autoConfirmMatched: {
      enabled: true,
      delayMinutes: 0
    },
    autoCartaInstruccion: false,
    autoConfirmDisputed: {
      enabled: false, 
      delayMinutes: 0
    }
  },
  alerts: {
    emailConfirmedTrades: {
      enabled: true,
      emails: []  // Will be populated with client admin email
    },
    emailDisputedTrades: {
      enabled: true,
      emails: []  // Will be populated with client admin email
    }
  },
  display: {
    theme: 'light',
    currency: 'CLP',
    timezone: 'America/Santiago',
    language: 'es'
  }
};
```

### Error Handling and Validation

#### Pre-creation Validation
- Check if Firebase Auth user exists for email
- Verify bank/client doesn't already exist
- Validate required fields (tax ID format, SWIFT code format)
- Check dependencies (bank must exist before creating client)

#### Transaction Safety
- Use Firestore batch operations where possible
- Rollback on partial failures
- Log all creation steps for debugging

### Firebase Auth Integration

#### Firebase Auth Integration
```javascript
// Production Firebase Auth integration (no emulator)
// Scripts will look up users directly in Firebase Auth by email
// and get their UIDs for Firestore user profile creation

const EMAIL_TO_BANK_MAPPING = {
  '@bancoabc.cl': 'banco-abc',
  '@bci.cl': 'banco-bci', 
  '@itau.cl': 'banco-itau'
};

function getBankFromEmail(email) {
  for (const [domain, bankId] of Object.entries(EMAIL_TO_BANK_MAPPING)) {
    if (email.includes(domain)) {
      return bankId;
    }
  }
  return null;
}
```

## Usage Examples

### Creating BCI Bank and Admin (Interactive CLI)
```bash
# 1. Create the bank (will prompt for details)
node scripts/create-bank.js

# Script will ask:
# ? Bank ID: banco-bci
# ? Bank Name: BCI
# ? Tax ID (RUT): 97.004.000-5
# ? SWIFT Code: BCHCCLRM
# ? Country: CL

# 2. Create bank admin (will prompt for details)
node scripts/create-bank-user.js

# Script will ask:
# ? Email: admin@bci.cl
# ? First Name: María
# ? Last Name: Silva
# ? Bank ID: banco-bci
# ? Role: bank_admin
```

### Creating Client for BCI
```bash
# 1. Create the client
node scripts/create-client.js \
  --clientId="acme-corp" \
  --name="ACME Corporation" \
  --taxId="76.456.789-0" \
  --bankId="banco-bci"

# 2. Create client admin
node scripts/create-client-user.js \
  --email="admin@acme.cl" \
  --firstName="Juan" \
  --lastName="Pérez" \
  --clientId="acme-corp" \
  --role="client_admin"
```

### Batch Creation Script
```bash
# Create multiple entities at once
node scripts/batch-create.js --config="bci-setup.json"
```

Where `bci-setup.json` contains:
```json
{
  "bank": {
    "bankId": "banco-bci",
    "name": "Banco BCI",
    "taxId": "97.004.000-5",
    "swiftCode": "BCHCCLRM"
  },
  "bankAdmin": {
    "email": "admin@bci.cl",
    "firstName": "María",
    "lastName": "Silva"
  },
  "clients": [
    {
      "clientId": "acme-corp",
      "name": "ACME Corporation", 
      "taxId": "76.456.789-0",
      "adminUser": {
        "email": "admin@acme.cl",
        "firstName": "Juan",
        "lastName": "Pérez"
      }
    }
  ]
}
```

## Integration with Existing System

### Updating Main Seed Script
- Keep `seed-demo-data.js` for full system setup
- Have it call individual creation scripts internally
- Maintain backwards compatibility

### Database Migration Support
- Scripts should be idempotent (safe to run multiple times)
- Check for existing data before creating
- Support update modes for modifying existing entities

## File Structure
```
scripts/
├── create-bank.js              # Individual bank creation
├── create-bank-user.js         # Bank admin user creation  
├── create-client.js            # Individual client creation
├── create-client-user.js       # Client user creation
├── batch-create.js            # Bulk creation from config
├── templates/                 # Default templates and settings
│   ├── bank-defaults.js
│   ├── client-defaults.js
│   └── settlement-templates.js
├── utils/                     # Shared utilities
│   ├── firebase-helper.js     # Firebase connection and auth
│   ├── validation.js          # Input validation
│   └── uid-resolver.js        # Enhanced UID resolution
└── configs/                   # Example configurations
    ├── bci-setup.json
    └── itau-setup.json
```

## Next Steps

1. **Review and refine** this approach
2. **Create base utility functions** (Firebase connection, validation)
3. **Implement individual creation scripts** starting with banks
4. **Test with BCI and Itaú creation**
5. **Create batch processing capability**
6. **Update documentation and examples**

## ✅ **Decisions Made Based on BC Feedback**

1. ✅ **Interactive CLI**: Scripts ask questions and take user answers
2. ✅ **No rollback scripts**: Keep it simple, no cleanup needed  
3. ✅ **Production Firebase only**: No emulator support, direct Firebase Auth + CMEK database
4. ✅ **Use defaults**: Minimal customization, sensible defaults applied automatically
5. ✅ **No demo data integration**: Not needed since we're using production Firebase
6. ✅ **Simplified bank creation**: Only main document + system settings (no segments/letters)
7. ✅ **Simplified client creation**: Only main document + settings (no rules/accounts)