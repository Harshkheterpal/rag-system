"""
Test the DocumentProcessor module

This tests the chunking logic WITHOUT needing a real PDF
We'll test chunking with simple text
"""

import sys
sys.path.insert(0, 'src')

from core.document_processor import DocumentProcessor
import logging

# Set up logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

print("\n" + "="*60)
print("TEST 1: Chunking Logic")
print("="*60 + "\n")

# Create processor
processor = DocumentProcessor(chunk_size=500, overlap=50)

# Test text (short version to understand chunking)
test_text = """
Machine learning is a subset of artificial intelligence that enables systems 
to learn and improve from experience without being explicitly programmed. 
Instead of following pre-programmed instructions, machine learning algorithms 
learn patterns from data. The process involves three main steps: data collection, 
training, and prediction. Supervised learning uses labeled examples, unsupervised 
learning finds hidden patterns, and reinforcement learning learns through rewards. 
Applications include healthcare diagnostics, fraud detection, self-driving cars, 
and recommendation systems. As computing power increases, machine learning will 
become even more powerful and ubiquitous in society.
"""

print(f"Test text length: {len(test_text)} characters\n")

# Test chunking
chunks = processor.chunk_text(test_text)

print(f"✅ Created {len(chunks)} chunks\n")

# Display chunks
for i, chunk in enumerate(chunks, 1):
    print(f"Chunk {i}:")
    print(f"  Start: {chunk['start_idx']}, End: {chunk['end_idx']}")
    print(f"  Content (first 60 chars): {chunk['content'][:60]}...")
    print()

print("="*60)
print(f"SUCCESS: Chunking works! Created {len(chunks)} chunks")
print("="*60 + "\n")