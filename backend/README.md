# Backend - Client Confirmation Manager 2.0

Python FastAPI backend with Google Cloud Platform integration.

## Structure

- `src/api/` - API endpoints, middleware, and authentication decorators
- `src/services/` - Business logic services (email, parsing, comparison, etc.)
- `src/models/` - Data models and schemas
- `src/agents/` - Autonomous agents for email processing workflows
- `src/utils/` - Helper functions and utilities
- `src/config/` - Configuration management
- `tests/` - Unit and integration tests

## Key Features

- FastAPI with automatic OpenAPI documentation
- Firebase Admin SDK for authentication
- Google Firestore for data persistence
- Vertex AI for LLM-powered trade parsing
- Gmail API for email processing
- Agent-based architecture for email workflows

## Development

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```