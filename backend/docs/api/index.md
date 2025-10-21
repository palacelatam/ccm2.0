# API Reference

Complete REST API documentation for CCM 2.0 backend.

## Base URL

```
Development: http://localhost:8000/api/v1
Production: https://api.ccm.example.com/api/v1
```

## Authentication

All endpoints (except health and auth/verify) require Firebase authentication token:

```http
Authorization: Bearer {firebase_token}
```

## API Endpoints

### [Authentication](routes/auth.md)
User authentication and token verification.

- `POST /auth/verify` - Verify Firebase token
- `GET /auth/profile` - Get user profile
- `GET /auth/permissions` - Get user permissions

### [Users](routes/users.md)
User management and profiles.

- `GET /users/me` - Current user profile
- `PUT /users/me` - Update current user
- `GET /users/{uid}` - Get specific user

### [Clients](routes/clients.md)
Client operations and trade management.

- `GET /clients` - List all clients
- `GET /clients/{id}/settings` - Client settings
- `POST /clients/{id}/upload-trades` - Upload trades
- `POST /clients/{id}/upload-emails` - Upload confirmations

### [Banks](routes/banks.md)
Bank configuration and templates.

- `GET /banks/{id}` - Bank information
- `GET /banks/{id}/client-segments` - Client segments
- `GET /banks/{id}/settlement-letters` - Letter templates

### [Gmail](routes/gmail.md)
Email monitoring and management.

- `POST /gmail/check-now` - Manual email check
- `POST /gmail/start-monitoring` - Start monitoring
- `GET /gmail/status` - Service status

### [Events](routes/events.md)
Real-time notifications via SSE.

- `GET /events/stream` - SSE event stream
- `GET /events/stats` - Connection statistics

### [SMS](routes/sms.md)
SMS notification management.

- `POST /sms/test` - Send test SMS
- `GET /sms/validate` - Validate configuration

## Response Format

All responses follow this format:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data
  }
}
```

## Error Responses

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "errors": ["Detailed error 1", "Detailed error 2"]
}
```

## Common HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 413 | Payload Too Large - File too big |
| 422 | Unprocessable Entity - Validation failed |
| 500 | Internal Server Error |

## Rate Limiting

- **Gmail API**: 250 quota units per user per second
- **SMS API**: 10 messages per minute
- **File Uploads**: 10MB max file size
- **SSE Connections**: 100 concurrent per client

## Pagination

List endpoints support pagination:

```http
GET /api/v1/resource?page=1&page_size=20
```

Response includes pagination metadata:

```json
{
  "success": true,
  "data": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "has_next": true
}
```

## File Uploads

File upload endpoints use multipart/form-data:

```http
POST /api/v1/clients/{id}/upload-trades
Content-Type: multipart/form-data

file: trades.csv
overwrite: true
```

## Webhooks

The system can send webhooks for these events:

- Trade matched
- Trade disputed
- Settlement instruction generated
- Upload completed

Configure webhooks in client settings.

## API Versioning

The API uses URL versioning:

- Current: `/api/v1`
- Legacy: `/api/v0` (deprecated)

## SDK Support

Official SDKs available for:

- JavaScript/TypeScript
- Python
- Go

## OpenAPI Specification

Download the OpenAPI spec:

```
GET /openapi.json
```

View interactive docs:

```
GET /docs  # Swagger UI
GET /redoc # ReDoc
```