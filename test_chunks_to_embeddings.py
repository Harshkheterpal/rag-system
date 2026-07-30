"""
Test full pipeline: Chunks → Embeddings
"""

import sys
sys.path.insert(0, 'src')

import logging
from core.document_processor import DocumentProcessor
from core.embeddings import EmbeddingGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

print("\n" + "="*60)
print("FULL PIPELINE TEST: Chunks → Embeddings")
print("="*60 + "\n")

try:
    # Step 1: Create test chunks
    print("Step 1: Creating test chunks...")
    processor = DocumentProcessor(chunk_size=500, overlap=50)
    
    # Use sample text
    test_text = """
    Machine learning is a subset of artificial intelligence that enables 
    systems to learn and improve from experience without being explicitly 
    programmed. The process involves data collection, training, and prediction. 
    There are three main types: supervised learning, unsupervised learning, and 
    reinforcement learning. Applications include healthcare diagnostics, fraud 
    detection, self-driving cars, and recommendation systems. As computing 
    power increases, machine learning capabilities continue to expand rapidly 
    across all industries. The future of AI depends on advances in machine 
    learning and deep learning technologies.
    """
    
    chunks = processor.chunk_text(test_text)
    print(f"✅ Created {len(chunks)} chunks\n")
    
    # Step 2: Generate embeddings
    print("Step 2: Generating embeddings...")
    generator = EmbeddingGenerator()
    
    embedded_chunks = generator.embed_chunks(chunks)
    print(f"✅ Generated {len(embedded_chunks)} embeddings\n")
    
    # Step 3: Display results
    print("Results:")
    print("-" * 60)
    
    for i, chunk in enumerate(embedded_chunks, 1):
        print(f"\nChunk {i}:")
        print(f"  Content (first 50 chars): {chunk['content'][:50]}...")
        print(f"  Content length: {len(chunk['content'])} characters")
        print(f"  Embedding dimension: {len(chunk['embedding'])}")
        print(f"  Embedding (first 5 values): {chunk['embedding'][:5]}")
        print(f"  Metadata: {chunk['metadata']}")
    
    print("\n" + "="*60)
    print("✅ FULL PIPELINE SUCCESSFUL!")
    print("="*60)
    print(f"\nSummary:")
    print(f"  Total chunks: {len(embedded_chunks)}")
    print(f"  Each chunk has: content, embedding (1536 dims), metadata")
    print(f"  Ready for Pinecone storage (Day 10)!")
    print("\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()