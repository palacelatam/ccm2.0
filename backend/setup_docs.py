#!/usr/bin/env python3
"""
Setup script for MkDocs documentation
Run this to initialize the documentation structure and add docstrings
"""

import os
import subprocess
import sys
from pathlib import Path

def setup_mkdocs():
    """Setup MkDocs documentation for the backend"""

    print("🚀 Setting up MkDocs for CCM 2.0 Backend...")

    # Check if we're in the backend directory
    if not os.path.exists("src"):
        print("❌ Error: Please run this script from the backend directory")
        sys.exit(1)

    # Install documentation dependencies
    print("📦 Installing documentation dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-docs.txt"])

    # Create documentation directories
    docs_dirs = [
        "docs/getting-started",
        "docs/architecture",
        "docs/api/routes",
        "docs/services",
        "docs/models",
        "docs/config",
        "docs/development",
        "docs/deployment",
        "docs/guides"
    ]

    for dir_path in docs_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {dir_path}")

    # Create placeholder files for main sections
    placeholders = {
        "docs/getting-started/installation.md": "# Installation Guide\n\nTODO: Add installation instructions",
        "docs/getting-started/configuration.md": "# Configuration Guide\n\nTODO: Add configuration details",
        "docs/getting-started/quickstart.md": "# Quick Start\n\nTODO: Add quick start guide",
        "docs/architecture/overview.md": "# Architecture Overview\n\nTODO: Add architecture overview",
        "docs/api/index.md": "# API Reference\n\nComplete API documentation for all endpoints.",
        "docs/services/index.md": "# Services Documentation\n\nBusiness logic layer documentation.",
        "docs/models/index.md": "# Data Models\n\nPydantic model documentation.",
    }

    for file_path, content in placeholders.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ Created {file_path}")

    print("\n🎉 MkDocs setup complete!")
    print("\n📝 Next steps:")
    print("1. Run 'mkdocs serve' to start the documentation server")
    print("2. Visit http://localhost:8000 to view the documentation")
    print("3. Run 'python improve_docstrings.py' to add better docstrings to your code")
    print("4. Run 'mkdocs build' to generate static documentation")
    print("\n💡 Tips:")
    print("- Edit mkdocs.yml to customize the documentation structure")
    print("- Add docstrings in Google style format for best results")
    print("- Use markdown files in docs/ for additional documentation")

if __name__ == "__main__":
    setup_mkdocs()