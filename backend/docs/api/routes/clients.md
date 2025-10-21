# Clients API

API endpoints for client management and trade processing.

## Endpoints Overview

### Client Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/clients` | List all clients |
| GET | `/clients/{client_id}/settings` | Get client settings |
| PUT | `/clients/{client_id}/settings` | Update client settings |

### Trade Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/clients/{client_id}/unmatched-trades` | Get unmatched trades |
| GET | `/clients/{client_id}/matched-trades` | Get matched trades |
| POST | `/clients/{client_id}/upload-trades` | Upload CSV trades |
| POST | `/clients/{client_id}/upload-emails` | Upload email confirmations |
| DELETE | `/clients/{client_id}/unmatched-trades` | Delete all unmatched trades |
| POST | `/clients/{client_id}/process-matches` | Run matching algorithm |

### Bank Accounts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/clients/{client_id}/bank-accounts` | List accounts |
| POST | `/clients/{client_id}/bank-accounts` | Create account |
| GET | `/clients/{client_id}/bank-accounts/{account_id}` | Get account |
| PUT | `/clients/{client_id}/bank-accounts/{account_id}` | Update account |
| DELETE | `/clients/{client_id}/bank-accounts/{account_id}` | Delete account |

### Settlement Rules

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/clients/{client_id}/settlement-rules` | List rules |
| POST | `/clients/{client_id}/settlement-rules` | Create rule |
| GET | `/clients/{client_id}/settlement-rules/{rule_id}` | Get rule |
| PUT | `/clients/{client_id}/settlement-rules/{rule_id}` | Update rule |
| DELETE | `/clients/{client_id}/settlement-rules/{rule_id}` | Delete rule |

## Detailed Endpoint Documentation

### List All Clients

```http
GET /api/v1/clients
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "xyz-corp",
      "name": "XYZ Corporation",
      "organizationName": "XYZ Corp",
      "bankId": "bank-123",
      "confirmationEmail": "trades@xyz-corp.com",
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Upload Trades (CSV)

```http
POST /api/v1/clients/{client_id}/upload-trades
Content-Type: multipart/form-data
```

**Request:**
```
file: trades.csv (file upload)
overwrite: false (optional, default: false)
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully processed 150 trades",
  "data": {
    "records_processed": 150,
    "records_failed": 0,
    "matches_found": 45,
    "upload_session_id": "session-123"
  }
}
```

**CSV Format:**
```csv
TradeNumber,CounterpartyName,ProductType,TradeDate,ValueDate,Direction,Currency1,QuantityCurrency1,Currency2,ForwardPrice
T2024-001,Bank of America,Spot,01/03/2024,03/03/2024,Buy,USD,100000,CLP,950.50
T2024-002,Santander,Forward,01/03/2024,01/04/2024,Sell,EUR,50000,USD,1.0850
```

### Upload Email Confirmations

```http
POST /api/v1/clients/{client_id}/upload-emails
Content-Type: multipart/form-data
```

**Request:**
```
file: confirmation.msg or confirmation.pdf (file upload)
```

**Response:**
```json
{
  "success": true,
  "message": "Email processed successfully",
  "data": {
    "email_id": "email-456",
    "trades_extracted": 2,
    "matches_created": 2,
    "notifications_scheduled": 1
  }
}
```

### Get Client Settings

```http
GET /api/v1/clients/{client_id}/settings
```

**Response:**
```json
{
  "success": true,
  "data": {
    "automation": {
      "dataSharing": false,
      "autoConfirmMatched": {
        "enabled": true,
        "delayMinutes": 30
      },
      "autoCartaInstruccion": false,
      "autoConfirmDisputed": {
        "enabled": true,
        "delayMinutes": 60
      }
    },
    "alerts": {
      "emailConfirmedTrades": {
        "enabled": true,
        "emails": ["trading@xyz-corp.com"]
      },
      "emailDisputedTrades": {
        "enabled": true,
        "emails": ["risk@xyz-corp.com"]
      },
      "smsConfirmedTrades": {
        "enabled": false,
        "phones": []
      },
      "smsDisputedTrades": {
        "enabled": true,
        "phones": ["+56912345678"]
      }
    },
    "preferences": {
      "language": "es",
      "timezone": "America/Santiago",
      "dateFormat": "DD/MM/YYYY",
      "numberFormat": "1.234,56"
    }
  }
}
```

### Update Client Settings

```http
PUT /api/v1/clients/{client_id}/settings
Content-Type: application/json
```

**Request:**
```json
{
  "automation": {
    "autoConfirmMatched": {
      "enabled": true,
      "delayMinutes": 15
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Settings updated successfully",
  "data": {
    // Updated settings object
  }
}
```

### Create Bank Account

```http
POST /api/v1/clients/{client_id}/bank-accounts
Content-Type: application/json
```

**Request:**
```json
{
  "accountName": "Main USD Account",
  "bankName": "Bank of America",
  "swiftCode": "BOFAUS3N",
  "accountCurrency": "USD",
  "accountNumber": "123456789",
  "isDefault": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Bank account created successfully",
  "data": {
    "id": "account-789",
    "accountName": "Main USD Account",
    "bankName": "Bank of America",
    "swiftCode": "BOFAUS3N",
    "accountCurrency": "USD",
    "accountNumber": "****6789",
    "isDefault": true,
    "active": true,
    "createdAt": "2024-03-01T10:00:00Z"
  }
}
```

### Create Settlement Rule

```http
POST /api/v1/clients/{client_id}/settlement-rules
Content-Type: application/json
```

**Request:**
```json
{
  "name": "Default USD Spot",
  "priority": 1,
  "direction": "compra",
  "counterparty": "*",
  "product": "Spot",
  "modalidad": "entregaFisica",
  "cargarCurrency": "USD",
  "cargarBankName": "Bank of America",
  "cargarSwiftCode": "BOFAUS3N",
  "cargarAccountNumber": "123456789",
  "abonarCurrency": "CLP",
  "abonarBankName": "Banco Santander",
  "abonarSwiftCode": "BSCHCLRM",
  "abonarAccountNumber": "987654321"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Settlement rule created successfully",
  "data": {
    "id": "rule-123",
    "name": "Default USD Spot",
    "priority": 1,
    "active": true,
    "createdAt": "2024-03-01T10:00:00Z"
  }
}
```

### Get Matched Trades

```http
GET /api/v1/clients/{client_id}/matched-trades
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "tradeId": "trade-123",
      "tradeNumber": "T2024-001",
      "emailId": "email-456",
      "bankTradeNumber": "BK2024-001",
      "matchConfidence": 95,
      "status": "Confirmation OK",
      "discrepancies": [],
      "tradeDate": "2024-03-01",
      "counterpartyName": "Bank of America",
      "productType": "Spot",
      "direction": "Buy",
      "currency1": "USD",
      "quantityCurrency1": 100000,
      "currency2": "CLP",
      "forwardPrice": 950.50
    }
  ]
}
```

### Generate Settlement Instruction

```http
POST /api/v1/clients/{client_id}/settlement-instructions/generate
Content-Type: multipart/form-data
```

**Request:**
```
trade_number: T2024-001
bank_trade_number: BK2024-001 (optional)
email_id: email-456 (optional)
```

**Response:**
```json
{
  "success": true,
  "message": "Settlement instruction generated successfully",
  "data": {
    "document_url": "https://storage.googleapis.com/...",
    "storage_path": "settlements/xyz-corp/2024-03-01/instruction.pdf",
    "expiration": "2024-03-01T11:00:00Z"
  }
}
```

## Error Responses

### 400 Bad Request

```json
{
  "success": false,
  "message": "Invalid CSV format",
  "error_code": "INVALID_FORMAT",
  "errors": [
    "Missing required column: TradeNumber",
    "Invalid date format in row 5"
  ]
}
```

### 401 Unauthorized

```json
{
  "success": false,
  "message": "Invalid or expired token",
  "error_code": "INVALID_TOKEN"
}
```

### 403 Forbidden

```json
{
  "success": false,
  "message": "Insufficient permissions",
  "error_code": "FORBIDDEN",
  "details": {
    "required_permission": "manage_trades",
    "user_permissions": ["view_trades"]
  }
}
```

### 404 Not Found

```json
{
  "success": false,
  "message": "Client not found",
  "error_code": "NOT_FOUND"
}
```

### 413 Payload Too Large

```json
{
  "success": false,
  "message": "File too large",
  "error_code": "FILE_TOO_LARGE",
  "details": {
    "max_size_mb": 10,
    "file_size_mb": 15.5
  }
}
```

## Rate Limiting

- **Upload endpoints**: 10 requests per minute per client
- **List endpoints**: 100 requests per minute per client
- **Update endpoints**: 30 requests per minute per client

## Permissions

Required permissions for each endpoint group:

| Endpoint Group | Required Permission |
|----------------|-------------------|
| View operations | (authenticated) |
| Settings | `manage_settings` |
| Bank accounts | `manage_bank_accounts` |
| Settlement rules | `manage_settlement_rules` |
| Trade uploads | `manage_trades` |
| Email uploads | `manage_confirmations` |

## WebSocket Events

When operations complete, real-time events are sent via SSE:

```javascript
const eventSource = new EventSource('/api/v1/events/stream');

eventSource.addEventListener('trade_matched', (event) => {
  const data = JSON.parse(event.data);
  console.log('Trade matched:', data);
});
```

Event types:
- `upload_complete` - CSV/email upload finished
- `trade_matched` - Trade matched with confirmation
- `match_created` - New match created
- `settlement_generated` - Settlement instruction ready