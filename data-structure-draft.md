Data Structure Draft document

## 🔑 `roles`

Top-level collection to define all available roles and their specific permissions.

- **/roles/client_admin** (Using a readable ID for the document)
    - **displayName**: `string` (e.g., "Client Administrator")
    - **description**: `string` (e.g., "Full access to manage client settings and users.")
    - **permissions**: `array` of `string` (e.g., `["view_dashboard", "manage_settings", "manage_settlement_rules", "manage_bank_accounts", "manage_data_mappings"]`)
- **/roles/client_user** (Document)
    - **displayName**: `string` (e.g., "Client User")
    - **description**: `string` (e.g., "Can view trades and confirmations.")
    - **permissions**: `array` of `string` (e.g., `["view_dashboard"]`)
- **/roles/bank_admin** (Document)
    - **displayName**: `string` (e.g., "Bank Administrator")
    - **description**: `string` (e.g., "Manages bank-level settings like client segmentation.")
    - **permissions**: `array` of `string` (e.g., `["manage_client_segments", "manage_instruction_letters"]`)

---

## 🏛️ `banks`

Top-level collection to store bank entities.

- **/banks/{bankId}** (Document)
    - **name**: `string` (e.g., "Banco ABC")
    - **taxId**: `string` (e.g., "96.543.210-K")
    - **country**: `string` (e.g., "Chile")
    - **createdAt**: `timestamp`
    - **lastUpdatedAt**: `timestamp`
    - **lastUpdatedBy**: `reference` (to `/users/{userId}`)
    
    ---
    
    - **/banks/{bankId}/clientSegments** (Subcollection)
        - **/{segmentId}** (Document)
            - **name**: `string` (e.g., "Premium Clients")
            - **description**: `string` (e.g., "High-value clients with preferential treatment")
            - **createdAt**: `timestamp`
            - **lastUpdatedAt**: `timestamp`
            - **lastUpdatedBy**: `reference` (to `/users/{userId}`)
    - **/banks/{bankId}/settlementInstructionLetters** (Subcollection)
        - **/{letterId}** (Document)
            - **active**: `boolean`
            - **priority**: `number`
            - **ruleName**: `string`
            - **product**: `string`
            - **clientSegmentId**: `reference` (to `/banks/{bankId}/clientSegments/{segmentId}`)
            - **documentName**: `string`
            - **documentUrl**: `string`
            - **createdAt**: `timestamp`
            - **lastUpdatedAt**: `timestamp`
            - **lastUpdatedBy**: `reference` (to `/users/{userId}`)

---

## 🏢 `clients`

Top-level collection to store client companies.

- **/clients/{clientId}** (Document)
    - **name**: `string` (e.g., "Empresa Minera Los Andes S.A.")
    - **taxId**: `string` (e.g., "76.123.456-7")
    - **bankId**: `reference` (to `/banks/{bankId}`)
    - **clientSegmentId**: `reference` (to `/banks/{bankId}/clientSegments/{segmentId}`)
    - **createdAt**: `timestamp`
    - **lastUpdatedAt**: `timestamp`
    - **lastUpdatedBy**: `reference` (to `/users/{userId}`)
    
    ---
    
    - **/clients/{clientId}/settings** (Subcollection)
        - **/configuration** (A single document with a fixed ID)
            - **automation**: `map`
                - **dataSharing**: `boolean`
                - **autoConfirmMatched**: `map`
                    - **enabled**: `boolean`
                    - **delayMinutes**: `number`
                - **autoCartaInstruccion**: `boolean`
                - **autoConfirmDisputed**: `map`
                    - **enabled**: `boolean`
                    - **delayMinutes**: `number`
            - **alerts**: `map`
                - **emailConfirmedTrades**: `map`
                    - **enabled**: `boolean`
                    - **emails**: `array` of `string`
                - **emailDisputedTrades**: `map`
                    - **enabled**: `boolean`
                    - **emails**: `array` of `string`
                - **smsConfirmedTrades**: `map`
                    - **enabled**: `boolean`
                    - **phones**: `array` of `string`
                - **smsDisputedTrades**: `map`
                    - **enabled**: `boolean`
                    - **phones**: `array` of `string`
            - **lastUpdatedAt**: `timestamp`
            - **lastUpdatedBy**: `reference` (to `/users/{userId}`)
    - **/clients/{clientId}/bankAccounts** (Subcollection)
        - **/{accountId}** (Document)
            - **active**: `boolean`
            - **accountName**: `string`
            - **bankName**: `string`
            - **swiftCode**: `string`
            - **accountCurrency**: `string`
            - **accountNumber**: `string`
            - **createdAt**: `timestamp`
            - **lastUpdatedAt**: `timestamp`
            - **lastUpdatedBy**: `reference` (to `/users/{userId}`)
    - **/clients/{clientId}/settlementRules** (Subcollection)
        - **/{ruleId}** (Document)
            - **active**: `boolean`
            - **priority**: `number`
            - **name**: `string`
            - **counterparty**: `string`
            - **cashflowCurrency**: `string`
            - **direction**: `string`
            - **product**: `string`
            - **bankAccountId**: `reference` (to `/clients/{clientId}/bankAccounts/{accountId}`)
            - **createdAt**: `timestamp`
            - **lastUpdatedAt**: `timestamp`
            - **lastUpdatedBy**: `reference` (to `/users/{userId}`)
    - **/clients/{clientId}/dataMappings** (Subcollection)
        - **/{mappingId}** (Document)
            - **name**: `string`
            - **description**: `string`
            - **fileType**: `string`
            - **fieldMappings**: `array` (of map objects)
            - **createdAt**: `timestamp`
            - **lastUpdatedAt**: `timestamp`
            - **lastUpdatedBy**: `reference` (to `/users/{userId}`)

---

## 👤 `users`

Top-level collection to store all application users.

- **/users/{userId}** (Document ID should be the Firebase Auth UID)
    - **firstName**: `string` (e.g., "Admin")
    - **lastName**: `string` (e.g., "Usuario")
    - **email**: `string` (e.g., "[admin.user@xyz.cl](mailto:admin.user@xyz.cl)")
    - **roles**: `array` of `reference` (e.g., `[/roles/client_admin, /roles/client_user]`)
    - **bankId**: `reference` (to `/banks/{bankId}`)
    - **clientId**: `reference` (to `/clients/{clientId}`)
    - **createdAt**: `timestamp`
    - **lastUpdatedAt**: `timestamp`
    - **lastUpdatedBy**: `reference` (to `/users/{userId}`)