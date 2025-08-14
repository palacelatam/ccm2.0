# Gmail Integration for Automated Email Processing

## Overview

The Gmail integration allows the CCM system to automatically monitor a Gmail inbox (`confirmaciones_dev@palace.cl`) and process incoming trade confirmation emails in near real-time.

## Architecture

```
Gmail Inbox → Gmail API → Gmail Service → Existing Email Processing Pipeline
                              ↓
                    Extract PDFs & Metadata
                              ↓
                    Process via LLM (Claude)
                              ↓
                    Store in Firestore
                              ↓
                    Match with trades
```

## Setup Instructions

### 1. Enable Gmail API and Create Service Account

Follow the instructions in `setup-gmail-api.md` to:
1. Enable Gmail API in GCP project `ccm-dev-pool`
2. Create a service account with domain-wide delegation
3. Configure Google Workspace admin console
4. Download the service account JSON key

### 2. Configure Environment

Place the service account JSON file in the backend directory and set the environment variable:

```bash
# .env file
GMAIL_SERVICE_ACCOUNT_PATH=gmail-service-account.json
```

### 3. Start the Backend

The Gmail service will automatically initialize on startup if the service account is configured:

```bash
cd backend
python src/main.py
```

## API Endpoints

All Gmail endpoints require admin authentication.

### Check for New Emails Manually
```http
POST /api/v1/gmail/check-now
Authorization: Bearer {token}
```

### Start Monitoring
```http
POST /api/v1/gmail/start-monitoring
Content-Type: application/json
Authorization: Bearer {token}

{
    "check_interval": 30  // seconds between checks (min: 10, max: 3600)
}
```

### Stop Monitoring
```http
POST /api/v1/gmail/stop-monitoring
Authorization: Bearer {token}
```

### Get Status
```http
GET /api/v1/gmail/status
Authorization: Bearer {token}
```

## How It Works

### Email Detection
1. Service monitors `confirmaciones_dev@palace.cl` inbox
2. Uses Gmail History API to detect new messages efficiently
3. Extracts emails where monitoring address is in To/CC

### Client Identification
- Extracts client email from To: field (excluding monitoring address)
- Maps email to client ID (currently hardcoded to `dev-client-001`)
- TODO: Implement database lookup for email-to-client mapping

### Processing Flow
1. **Extract Email Data**: Sender, subject, date, body
2. **Extract PDF Attachments**: Downloads all PDF attachments
3. **Process PDFs**: Uses existing `EmailParserService` to extract data
4. **LLM Processing**: Sends to Claude for trade extraction
5. **Store in Database**: Saves to Firestore with session tracking
6. **Auto-Matching**: Triggers matching with existing trades

### Monitoring Options
- **Near Real-Time**: Default 30-second intervals
- **Configurable**: 10 seconds to 1 hour
- **Background Task**: Runs asynchronously without blocking API

## Testing

### Manual Test Script
```bash
cd backend
python test_gmail_service.py
```

### Test Process
1. Send test email with PDF attachment to `confirmaciones_dev@palace.cl`
2. CC the client's email address
3. Run test script or use API to check for new emails
4. Verify processing in logs and database

## Implementation Details

### Key Files
- `src/services/gmail_service.py` - Gmail API integration
- `src/api/routes/gmail.py` - API endpoints
- `src/services/client_service.py` - `process_gmail_attachment()` adapter
- `setup-gmail-api.md` - Setup instructions

### Design Principles
- **No Code Duplication**: Reuses existing email processing pipeline
- **Modular**: Gmail is just another email source
- **Configurable**: Flexible monitoring intervals
- **Resilient**: Handles errors gracefully, continues monitoring

## Future Enhancements

1. **Client Email Mapping**: 
   - Add email field to client model
   - Implement database lookup in `_determine_client_id()`

2. **Production Setup**:
   - Use `confirmaciones@palace.cl` for production
   - Separate service accounts per environment

3. **Enhanced Monitoring**:
   - Webhook support for instant notifications
   - Multiple inbox monitoring
   - Email filtering rules

4. **Metrics & Logging**:
   - Processing statistics dashboard
   - Alert on processing failures
   - Performance monitoring

## Troubleshooting

### Service Account Not Found
- Ensure `gmail-service-account.json` exists in backend directory
- Check `GMAIL_SERVICE_ACCOUNT_PATH` environment variable

### Authentication Failed
- Verify domain-wide delegation is enabled
- Check OAuth scopes in Google Workspace admin
- Ensure service account has correct permissions

### No Emails Detected
- Verify emails are sent to `confirmaciones_dev@palace.cl`
- Check Gmail API quotas in GCP
- Review logs for error messages

### Processing Failures
- Check LLM API keys (Claude/Anthropic)
- Verify Firestore permissions
- Review PDF attachment format