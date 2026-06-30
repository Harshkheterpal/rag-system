"""
Test script to verify all installations are working
Run this to make sure everything is set up correctly
"""

import sys
import os

print("=" * 60)
print("RAG SYSTEM - SETUP VERIFICATION TEST")
print("=" * 60)

# Test 1: Python version
print("\n1️⃣  PYTHON VERSION")
print(f"   Version: {sys.version}")
print(f"   ✅ PASS" if sys.version_info >= (3, 12) else "   ❌ FAIL - Need Python 3.12+")

# Test 2: Virtual environment
print("\n2️⃣  VIRTUAL ENVIRONMENT")
in_venv = hasattr(sys, 'real_prefix') or (
    hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
)
print(f"   In venv: {in_venv}")
print(f"   ✅ PASS" if in_venv else "   ❌ FAIL - Not in virtual environment")

# Test 3: Key imports
print("\n3️⃣  CORE IMPORTS")
try:
    import openai
    print(f"   ✅ openai ({openai.__version__})")
except ImportError as e:
    print(f"   ❌ openai - {e}")

try:
    import langchain
    print(f"   ✅ langchain ({langchain.__version__})")
except ImportError as e:
    print(f"   ❌ langchain - {e}")

try:
    from pinecone import Pinecone
    print(f"   ✅ pinecone")
except ImportError as e:
    print(f"   ❌ pinecone - {e}")

try:
    import fastapi
    print(f"   ✅ fastapi ({fastapi.__version__})")
except ImportError as e:
    print(f"   ❌ fastapi - {e}")

try:
    from PyPDF2 import PdfReader
    print(f"   ✅ PyPDF2")
except ImportError as e:
    print(f"   ❌ PyPDF2 - {e}")

try:
    from dotenv import load_dotenv
    print(f"   ✅ python-dotenv")
except ImportError as e:
    print(f"   ❌ python-dotenv - {e}")

# Test 4: Environment file
print("\n4️⃣  ENVIRONMENT FILES")
env_exists = os.path.exists(".env")
env_example_exists = os.path.exists(".env.example")

print(f"   .env exists: {env_exists}")
print(f"   ✅ PASS" if env_exists else "   ⚠️  Not found - Create .env with API keys")

print(f"   .env.example exists: {env_example_exists}")
print(f"   ✅ PASS" if env_example_exists else "   ⚠️  Not found")

# Test 5: Folder structure
print("\n5️⃣  FOLDER STRUCTURE")
required_dirs = ["src", "src/core", "src/api", "src/utils", "tests", "docs", "data"]
for dir_name in required_dirs:
    exists = os.path.exists(dir_name)
    symbol = "✅" if exists else "❌"
    print(f"   {symbol} {dir_name}/")

# Final summary
print("\n" + "=" * 60)
print("SETUP VERIFICATION COMPLETE")
print("=" * 60)
print("\n✅ If all checks pass, you're ready to start!")
print("❌ If anything failed, fix it before proceeding.")
print("\nNext: Create GitHub repo and make first commit")
print("=" * 60)