# Quick Start Guide

Get started with CCM 2.0 backend documentation in minutes.

## Prerequisites

- Python 3.8+
- pip
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourorg/ccm2.0.git
cd ccm2.0/backend
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install main dependencies
pip install -r requirements.txt

# Install documentation dependencies
pip install -r requirements-docs.txt
```

### 3. Set Up Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

Required environment variables:
```env
FIREBASE_PROJECT_ID=ccm-dev-pool
FIREBASE_DATABASE_ID=ccm-development
ANTHROPIC_API_KEY=your-api-key
BIRD_API_KEY=your-sms-api-key
```

## Running the Documentation Server

### Local Development

```bash
# Start the documentation server
mkdocs serve

# Documentation will be available at:
# http://localhost:8002
```

**For Windows users - Use the batch files:**
```cmd
# Option 1: Simple launcher
launch_docs.bat

# Option 2: Interactive manager with menu
docs_manager.bat

# Option 3: Quick launch (no checks)
docs_quick.bat
```

### Build Static Documentation

```bash
# Build the documentation
mkdocs build

# Output will be in site/ directory
ls site/
```

## Viewing API Documentation

### Interactive API Docs

Start the backend server:

```bash
# Run the FastAPI server
python src/main.py

# API documentation available at:
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

### Using the Documentation

1. **Browse by Category**: Use the navigation menu to find specific topics
2. **Search**: Use the search bar to find specific functions or concepts
3. **Code Examples**: Copy code examples directly from the documentation
4. **API Reference**: View auto-generated API documentation from docstrings

## Writing Documentation

### Adding Docstrings

Use Google-style docstrings for best compatibility:

```python
def process_trade(trade_id: str, amount: float) -> Dict[str, Any]:
    """
    Process a single trade transaction.

    Args:
        trade_id: Unique identifier for the trade
        amount: Trade amount in base currency

    Returns:
        Dict containing:
            - status: Processing status
            - result: Processing result

    Raises:
        ValueError: If trade_id is invalid
        HTTPException: If processing fails

    Example:
        ```python
        result = process_trade("T2024-001", 100000.0)
        print(result['status'])
        ```
    """
    # Implementation here
    pass
```

### Creating Documentation Pages

Create a new markdown file in the appropriate directory:

```markdown
# Page Title

Brief description of the topic.

## Section 1

Content here...

### Subsection

More detailed content...

## Code Examples

```python
# Example code here
```
```

### Using MkDocstrings

Reference Python objects in markdown:

```markdown
# Service Documentation

::: services.client_service.ClientService
    options:
      show_source: false
      members:
        - process_csv_upload
        - process_email_upload
```

## Testing Documentation

### Check Docstring Coverage

```bash
# Install interrogate
pip install interrogate

# Check coverage
interrogate -v src/

# Generate badge
interrogate --generate-badge docs/badges/
```

### Validate Documentation Build

```bash
# Build with strict mode
mkdocs build --strict

# Check for warnings
mkdocs build --verbose 2>&1 | grep WARNING
```

## Deployment

### GitHub Pages

Documentation automatically deploys on merge to main:

1. Push changes to main branch
2. GitHub Actions builds documentation
3. Deploys to GitHub Pages
4. Available at: https://yourorg.github.io/ccm2.0

### Manual Deployment

```bash
# Deploy to GitHub Pages
mkdocs gh-deploy

# Deploy with specific message
mkdocs gh-deploy -m "Update documentation"
```

## Best Practices

### 1. Keep Docstrings Updated

- Update docstrings when changing function signatures
- Include examples for complex functions
- Document all public methods

### 2. Use Type Hints

```python
from typing import Dict, List, Optional

def get_trades(client_id: str) -> List[Dict[str, Any]]:
    """Get all trades for a client."""
    pass
```

### 3. Include Examples

```python
def complex_function():
    """
    Complex function description.

    Example:
        >>> result = complex_function()
        >>> print(result)
        {'status': 'success'}
    """
    pass
```

### 4. Document Exceptions

```python
def risky_operation():
    """
    Perform risky operation.

    Raises:
        ValueError: When input is invalid
        ConnectionError: When database is unavailable
        HTTPException: When API call fails
    """
    pass
```

## Troubleshooting

### Common Issues

**MkDocs won't start:**
```bash
# Check if port 8000 is in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Use different port
mkdocs serve -a localhost:8001
```

**Import errors in documentation:**
```bash
# Ensure backend is in Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Or install package in development mode
pip install -e .
```

**Documentation not updating:**
```bash
# Clear cache
rm -rf site/
mkdocs build --clean

# Force rebuild
mkdocs serve --dirtyreload
```

## Additional Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [MkDocstrings Documentation](https://mkdocstrings.github.io/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [Google Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

## Getting Help

- Check the [FAQ](../guides/faq.md)
- Search existing [GitHub Issues](https://github.com/yourorg/ccm2.0/issues)
- Contact the development team

## Next Steps

1. [Set up your development environment](installation.md)
2. [Learn about the architecture](../architecture/overview.md)
3. [Explore the API](../api/index.md)
4. [Read the service documentation](../services/index.md)