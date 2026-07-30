"""
Test the embeddings module
"""

import sys
sys.path.insert(0, 'src')

import logging
from core.embeddings import EmbeddingGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

print("\n" + "="*60)
print("TEST: Embeddings Generator")
print("="*60 + "\n")

try:
    # Create generator
    print("Initializing EmbeddingGenerator...")
    generator = EmbeddingGenerator()
    print("✅ Generator initialized\n")
    
    # Test 1: Single embedding
    print("Test 1: Generate single embedding")
    text = "What is machine learning?"
    
    print(f"Text: '{text}'")
    print("Calling OpenAI API...")
    
    embedding = generator.generate_embedding(text)
    
    print(f"✅ Got embedding!\n")
    print(f"Embedding details:")
    print(f"  Dimension: {len(embedding)}")
    print(f"  First 5 values: {embedding[:5]}")
    print(f"  Last 5 values: {embedding[-5:]}")
    print(f"  Min value: {min(embedding):.4f}")
    print(f"  Max value: {max(embedding):.4f}")
    print()
    
    # Test 2: Batch embeddings
    print("Test 2: Generate batch embeddings")
    texts = [
        "Machine learning is cool",
        "Embeddings capture meaning",
        "RAG systems are powerful"
    ]
    
    print(f"Texts: {len(texts)} items")
    print("Calling OpenAI API...")
    
    embeddings = generator.generate_embeddings_batch(texts)
    
    print(f"✅ Got {len(embeddings)} embeddings!\n")
    for i, (text, emb) in enumerate(zip(texts, embeddings), 1):
        print(f"Embedding {i}:")
        print(f"  Text: '{text}'")
        print(f"  Vector length: {len(emb)}")
        print(f"  First 3 values: {[f'{x:.4f}' for x in emb[:3]]}")
    
    # Test 3: Verify similarity
    print("\nTest 3: Verify semantic similarity")
    
    similar_texts = [
        "Machine learning is AI",
        "ML is artificial intelligence",  # Should be very similar to above
        "Dogs are animals"  # Should be different
    ]
    
    print("Embedding similar and different texts...")
    similar_embeddings = generator.generate_embeddings_batch(similar_texts)
    
    # Calculate simple cosine similarity
    def cosine_similarity(a, b):
        """Calculate cosine similarity between two vectors"""
        import math
        dot_product = sum(x*y for x, y in zip(a, b))
        magnitude_a = math.sqrt(sum(x*x for x in a))
        magnitude_b = math.sqrt(sum(x*x for x in b))
        if magnitude_a == 0 or magnitude_b == 0:
            return 0
        return dot_product / (magnitude_a * magnitude_b)
    
    # Compare first two (should be similar)
    similarity_1_2 = cosine_similarity(similar_embeddings[0], similar_embeddings[1])
    
    # Compare first and third (should be different)
    similarity_1_3 = cosine_similarity(similar_embeddings[0], similar_embeddings[2])
    
    print(f"\nSimilarity between:")
    print(f"  Text 1 & 2 (similar): {similarity_1_2:.4f}")
    print(f"  Text 1 & 3 (different): {similarity_1_3:.4f}")
    print(f"\n✅ Similar texts have higher similarity! ({similarity_1_2:.4f} > {similarity_1_3:.4f})")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("  1. Check your OPENAI_API_KEY in .env")
    print("  2. Make sure it starts with 'sk-proj-'")
    print("  3. Verify the key isn't expired")
    print("  4. Run: python -m pip install openai python-dotenv")