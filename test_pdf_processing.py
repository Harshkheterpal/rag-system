"""
Test reading and chunking an actual PDF
"""

import sys
sys.path.insert(0, 'src')

from core.document_processor import DocumentProcessor
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

print("\n" + "="*60)
print("TEST 2: PDF Processing (Real File)")
print("="*60 + "\n")

# Create processor
processor = DocumentProcessor(chunk_size=500, overlap=50)

# Check if test PDF exists
pdf_path = "sample.pdf"

if not Path(pdf_path).exists():
    print(f"⚠️  {pdf_path} not found")
    print("To test with a real PDF:")
    print("  1. Download any PDF file")
    print("  2. Place it in: C:\\Users\\HKheterpal\\Desktop\\rag-system\\")
    print("  3. Rename it to: sample.pdf")
    print("  4. Run this script again")
    print("\nFor now, testing PDF reading logic only...")
    
else:
    print(f"Found {pdf_path}!\n")
    
    try:
        # Process the PDF
        chunks = processor.process_pdf(pdf_path)
        
        print(f"✅ Successfully processed PDF!")
        print(f"📊 Created {len(chunks)} chunks\n")
        
        # Show first 3 chunks
        for i, chunk in enumerate(chunks[:3], 1):
            print(f"Chunk {i}:")
            print(f"  Length: {len(chunk['content'])} characters")
            print(f"  Preview: {chunk['content'][:80]}...")
            print()
        
        print("="*60)
        print("✅ PDF PROCESSING SUCCESSFUL!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure the PDF is not corrupted")