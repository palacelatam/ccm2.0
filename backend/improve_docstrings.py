#!/usr/bin/env python3
"""
Script to add/improve docstrings in the backend code
This will help mkdocstrings generate better documentation
"""

import os
import ast
import textwrap
from pathlib import Path

# Example docstring templates for different components
DOCSTRING_TEMPLATES = {
    "service_class": '''"""
    {class_name} handles {purpose}.

    This service provides functionality for {functionality}.

    Attributes:
        db: Firestore client instance
        logger: Logger instance for this service

    Example:
        ```python
        service = {class_name}()
        result = await service.{example_method}()
        ```
    """''',

    "async_method": '''"""
    {description}

    Args:
        {args}

    Returns:
        {returns}

    Raises:
        HTTPException: {error_condition}

    Example:
        ```python
        {example}
        ```
    """''',

    "route_function": '''"""
    {description}

    This endpoint {functionality}.

    Args:
        {args}

    Returns:
        APIResponse[{return_type}]: {return_description}

    Raises:
        HTTPException:
            - 400: Bad request - {bad_request_reason}
            - 401: Unauthorized - Invalid or missing token
            - 403: Forbidden - Insufficient permissions
            - 404: Not found - {not_found_reason}
            - 500: Internal server error

    Example:
        ```http
        {http_method} /api/v1/{path}
        Authorization: Bearer {{token}}
        Content-Type: application/json

        {request_body}
        ```

    Response:
        ```json
        {response_example}
        ```
    """''',

    "model_class": '''"""
    {description}

    This model represents {representation}.

    Attributes:
        {attributes}

    Example:
        ```python
        {example}
        ```

    Note:
        {note}
    """''',
}

def analyze_client_service():
    """Analyze client_service.py and suggest docstring improvements"""

    file_path = "src/services/client_service.py"

    print(f"\n📝 Analyzing {file_path}...")
    print("=" * 60)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    tree = ast.parse(content)

    suggestions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if not ast.get_docstring(node):
                suggestions.append(f"❌ Class '{node.name}' is missing a docstring")
            else:
                current_doc = ast.get_docstring(node)
                if len(current_doc) < 50:
                    suggestions.append(f"⚠️  Class '{node.name}' has a minimal docstring")

        elif isinstance(node, ast.AsyncFunctionDef) or isinstance(node, ast.FunctionDef):
            if not node.name.startswith('_'):  # Skip private methods
                if not ast.get_docstring(node):
                    suggestions.append(f"❌ Method '{node.name}' is missing a docstring")
                else:
                    current_doc = ast.get_docstring(node)
                    # Check for Google-style docstring sections
                    if "Args:" not in current_doc and len(node.args.args) > 1:
                        suggestions.append(f"⚠️  Method '{node.name}' docstring missing 'Args:' section")
                    if "Returns:" not in current_doc:
                        suggestions.append(f"⚠️  Method '{node.name}' docstring missing 'Returns:' section")

    print("\n🔍 Analysis Results:")
    for suggestion in suggestions[:20]:  # Show first 20 suggestions
        print(f"  {suggestion}")

    if len(suggestions) > 20:
        print(f"\n  ... and {len(suggestions) - 20} more issues")

    print("\n💡 Suggested improvements for key methods:")
    print("-" * 60)

    # Example improved docstring for a key method
    example_docstring = '''
async def process_csv_upload(
    self,
    client_id: str,
    csv_content: str,
    filename: str,
    overwrite: bool = False,
    uploaded_by: str = None
) -> Dict[str, Any]:
    """
    Process CSV trade upload and perform automatic matching.

    This method handles the complete workflow for processing client trade
    uploads including parsing, validation, storage, and automatic matching
    with existing email confirmations.

    Args:
        client_id: The unique identifier of the client
        csv_content: The raw CSV content as a string
        filename: Original filename of the uploaded CSV
        overwrite: If True, deletes existing unmatched trades before import
        uploaded_by: UID of the user performing the upload

    Returns:
        Dict containing:
            - success (bool): Whether processing was successful
            - message (str): Status message
            - records_processed (int): Number of trades processed
            - records_failed (int): Number of trades that failed
            - matches_found (int): Number of automatic matches found
            - upload_session_id (str): Unique session identifier

    Raises:
        HTTPException:
            - 400: Invalid CSV format or missing required fields
            - 404: Client not found
            - 500: Database or processing error

    Example:
        ```python
        service = ClientService()
        result = await service.process_csv_upload(
            client_id="xyz-corp",
            csv_content=csv_data,
            filename="trades_2024.csv",
            overwrite=False,
            uploaded_by="user-123"
        )

        if result['success']:
            print(f"Processed {result['records_processed']} trades")
            print(f"Found {result['matches_found']} matches")
        ```

    Note:
        Large CSV files (>10,000 rows) may take several minutes to process.
        Consider implementing progress tracking for better UX.
    """
    '''

    print(textwrap.dedent(example_docstring))

    print("\n📚 Benefits of improved docstrings:")
    print("  ✅ Better IDE autocomplete and hints")
    print("  ✅ Automatic API documentation generation")
    print("  ✅ Easier onboarding for new developers")
    print("  ✅ Reduced need for external documentation")
    print("  ✅ Type hints validation with mypy")

def generate_service_docs():
    """Generate documentation stubs for all services"""

    services_dir = Path("src/services")
    docs_dir = Path("docs/services")

    for service_file in services_dir.glob("*.py"):
        if service_file.name.startswith("__"):
            continue

        service_name = service_file.stem
        doc_file = docs_dir / f"{service_name}.md"

        if not doc_file.exists():
            doc_content = f"""# {service_name.replace('_', ' ').title()} Documentation

::: services.{service_name}
    options:
      show_source: false
      show_bases: false
      members_order: source
      group_by_category: true
"""
            doc_file.write_text(doc_content)
            print(f"✅ Created documentation for {service_name}")

if __name__ == "__main__":
    print("🔧 Docstring Improvement Tool for CCM 2.0 Backend")
    print("=" * 60)

    # Analyze the large ClientService
    analyze_client_service()

    print("\n" + "=" * 60)
    print("\n🎯 Recommendations:")
    print("\n1. Start with the most critical public methods")
    print("2. Use Google-style docstrings for consistency")
    print("3. Include Args, Returns, Raises, and Example sections")
    print("4. Add type hints to all function signatures")
    print("5. Document complex business logic inline with comments")

    print("\n📝 Example Google-style docstring format:")
    print("-" * 40)
    print('''
def method_name(self, param1: str, param2: int) -> Dict[str, Any]:
    """One-line summary.

    Extended description explaining the method's purpose
    and any important details.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of the return value

    Raises:
        ValueError: When validation fails
        HTTPException: When API errors occur

    Example:
        ```python
        result = service.method_name("value", 42)
        ```
    """
    ''')

    # Generate documentation files for services
    print("\n📁 Generating service documentation files...")
    generate_service_docs()