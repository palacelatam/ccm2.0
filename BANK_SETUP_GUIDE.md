# Bank Setup and Entity Creation Guide

This document provides a comprehensive guide for setting up banks, bank users, and counterparty mappings in the CCM2.0 system.

## Overview

The system requires three main entities to be created for full bank integration:
1. **Firebase Auth Users** - Authentication accounts for bank admins
2. **Bank Documents** - Bank records in Firestore with RUT and SWIFT codes
3. **Counterparty Mappings** - Client-specific aliases that map email variations to bank IDs

## Scripts Available

### 1. Firebase Auth User Creation
**Script:** `scripts/create-firebase-auth-users.py`

Creates Firebase Authentication accounts for all bank admin users.

```bash
cd scripts
python create-firebase-auth-users.py
```

**What it does:**
- Creates Firebase Auth users for all 14 Chilean bank admins
- Generates secure random passwords
- Uses email format: `admin@{bank-domain}.cl`
- Saves credentials to a timestamped file for secure sharing
- Skips users that already exist

**Output:** Creates a credentials file with usernames/passwords to share with banks.

### 2. Bank Document and User Profile Creation
**Script:** `scripts/setup-all-banks.py`

Creates bank documents in Firestore and links them to Firebase Auth users.

```bash
cd scripts
python setup-all-banks.py
```

**What it does:**
- Creates bank documents with real RUT and SWIFT codes
- Creates user profile documents linking Auth accounts to bank records
- Assigns `bank_admin` role to users
- Uses official bank names, RUTs, and SWIFT codes
- Skips banks/users that already exist

**Prerequisites:** Firebase Auth users must exist (run script #1 first).

### 3. Counterparty Mappings Creation
**Script:** `scripts/create-counterparty-mappings.py`

Creates client-specific aliases for banks to handle email variations.

```bash
cd scripts
python create-counterparty-mappings.py xyz-corp
# or run without arguments to be prompted for client ID
python create-counterparty-mappings.py
```

**What it does:**
- Creates counterparty mappings for a specific client
- Maps common bank name variations to standardized bank IDs
- Includes RUT numbers (with and without dots)
- Handles various bank name formats found in emails
- Prevents duplicate mappings

## Complete Setup Process

### For New Bank Integration (All 14 Chilean Banks)

1. **Create Firebase Auth Users**
   ```bash
   cd scripts
   python create-firebase-auth-users.py
   ```
   - Review the generated credentials file
   - Securely share credentials with each bank
   - Delete the credentials file after sharing

2. **Create Bank Documents and Profiles**
   ```bash
   python setup-all-banks.py
   ```
   - Confirm that Auth users exist when prompted
   - Verify all banks and users are created successfully

3. **Create Counterparty Mappings per Client**
   ```bash
   python create-counterparty-mappings.py client-id
   ```
   - Run for each client that needs bank mappings
   - Review and customize aliases in the script if needed

### For Individual Client Setup

If you only need to add counterparty mappings for a new client:

```bash
cd scripts
python create-counterparty-mappings.py new-client-id
```

## Bank Information Reference

### Supported Banks (14 Chilean Banks)

| Bank ID | Official Name | Domain | RUT | SWIFT Code |
|---------|---------------|---------|-----|------------|
| banco-abc | Banco ABC | bancoabc.cl | 99.999.999-9 | TESTCLRM |
| banco-bice | Banco BICE | bice.cl | 97.080.000-K | BICECLRM |
| banco-btg-pactual | BTG Pactual | btgpactual.cl | 76.362.099-9 | BPABCLRM |
| banco-consorcio | Banco Consorcio | bancoconsorcio.cl | 99.500.410-0 | MNEXCLRM |
| banco-de-chile | Banco de Chile | bancochile.cl | 97.004.000-5 | BCHICLRM |
| banco-bci | Banco de Crédito e Inversiones | bci.cl | 97.006.000-6 | CREDCLRM |
| banco-estado | Banco del Estado de Chile | bancoestado.cl | 97.030.000-7 | BECHCLRM |
| banco-falabella | Banco Falabella | bancofalabella.cl | 96.509.660-4 | FALACLRM |
| banco-internacional | Banco Internacional | internacional.cl | 97.011.000-3 | BICHCLRM |
| banco-itau | Banco Itaú Chile | itau.cl | 97.023.000-9 | ITAUCLRM |
| banco-ripley | Banco Ripley | bancoripley.cl | 97.947.000-2 | RPLYCLRM |
| banco-santander | Banco Santander Chile | santander.cl | 97.036.000-K | BSCHCLRM |
| banco-security | Banco Security | security.cl | 97.053.000-2 | BSCLCLRM |
| banco-hsbc | HSBC Bank Chile | hsbc.cl | 97.951.000-4 | BLICCLRM |
| banco-scotiabank | Scotiabank Chile | scotiabank.cl | 97.018.000-1 | BKSACLRM |
| banco-tanner | Tanner Banco Digital | tanner.cl | 99.999.999-9 | TANNCLRM |

### Admin Email Addresses

Each bank gets an admin user with email format: `admin@{domain}`

Examples:
- BCI: `admin@bci.cl`
- Santander: `admin@santander.cl`
- Itaú: `admin@itau.cl`

## Counterparty Mappings

### Purpose
Counterparty mappings resolve the issue where emails contain bank names in various formats that don't match our standardized bank IDs.

### Common Aliases Included
For each bank, the system maps common variations:

**Name Variations:**
- Short names (e.g., "BCI", "Santander")
- Full official names (e.g., "Banco de Crédito e Inversiones")
- Common abbreviations (e.g., "Scotia" for Scotiabank)

**RUT Variations:**
- With dots: `97.080.000-K`
- Without dots: `97080000-K`

**Special Cases:**
- Itaú: Includes historical names like "Itaú Corpbanca"
- Santander: Includes variations like "Banco Santander-Santiago"

### Database Structure
```
clients/{client-id}/counterpartyMappings/{mapping-id}
{
  "bankId": "banco-bci",
  "counterpartyName": "BCI",
  "createdAt": "2025-09-09T12:33:33Z",
  "createdBy": "counterparty-mapping-script"
}
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'config'**
   - Ensure scripts use `from src.config.firebase_config import ...`
   - Scripts should be run from the `scripts/` directory

2. **Firebase Auth user not found**
   - Run `create-firebase-auth-users.py` first
   - Verify users exist in Firebase Console > Authentication

3. **Client not found**
   - Ensure the client document exists in Firestore
   - Check client ID spelling and formatting

4. **Duplicate mappings**
   - Scripts automatically skip existing mappings
   - Review existing mappings in Firestore Console if needed

### Manual Verification

**Check Firebase Auth Users:**
```bash
# View in Firebase Console > Authentication > Users
```

**Check Bank Documents:**
```bash
# View in Firestore Console > banks collection
```

**Check Counterparty Mappings:**
```bash
# View in Firestore Console > clients/{client-id}/counterpartyMappings
```

## Maintenance

### Adding New Banks
1. Update bank lists in:
   - `backend/src/utils/bank_utils.py`
   - `frontend/src/utils/bankUtils.ts`
   - `frontend/src/pages/admin/AdminDashboard.tsx`
   - Script files: `setup-all-banks.py`, `create-firebase-auth-users.py`

2. Add aliases to `create-counterparty-mappings.py`

3. Run all three setup scripts

### Updating Bank Names
Ensure consistency across:
- Backend utilities
- Frontend utilities  
- Admin dashboard constants
- Setup scripts
- This documentation

---

*Last updated: September 2025*
*For technical support, refer to the Firebase Console and Firestore documentation.*