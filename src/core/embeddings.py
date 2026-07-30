"""
Embeddings Module
Converts text chunks into vector representations using OpenAI API

What this does:
1. Takes text chunks from DocumentProcessor
2. Sends to OpenAI's embedding model (Ada)
3. Gets back 1536-dimensional vectors
4. Each vector represents the MEANING of the text

Why embeddings?
- Numbers that capture semantic meaning
- Similar text gets similar vectors
- Enables fast similarity search later
- Foundation of RAG retrieval

Cost: $0.02 per 1M tokens (super cheap!)
"""

import logging
import os
from typing import List
import requests
import json

# Need to load environment variables
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Generates embeddings using OpenAI's embedding model via direct HTTP.
    
    Why Ada (text-embedding-3-small)?
    - CHEAP: $0.02 per 1M tokens
    - FAST: Instant results
    - GOOD: High quality embeddings
    - PROVEN: Used by millions in production
    
    Example:
        generator = EmbeddingGenerator()
        embedding = generator.generate_embedding("Hello world")
        print(len(embedding))  # 1536 (dimensions)
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize embedding generator.
        
        Args:
            api_key: OpenAI API key. If None, reads from .env
        
        Raises:
            ValueError: If API key not found
        """
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. "
                "Add it to .env file or pass as parameter"
            )
        
        # OpenAI API endpoint
        self.api_url = "https://api.openai.com/v1/embeddings"
        
        # Model to use (Ada is cheapest and fastest)
        self.model = "text-embedding-3-small"
        
        # Set up request headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"EmbeddingGenerator initialized with model: {self.model}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        What happens:
        1. Send text to OpenAI API
        2. Model processes it
        3. Returns vector (1536 numbers)
        
        Cost: ~$0.000000001 per embedding (literally pennies)
        
        Args:
            text: Text to convert to embedding
            
        Returns:
            List of 1536 float numbers (the embedding vector)
            
        Raises:
            Exception: If API call fails
        
        Example:
            text = "Machine learning is cool"
            embedding = generator.generate_embedding(text)
            print(embedding)  # [0.123, -0.456, 0.789, ...]
        """
        try:
            # Prepare request payload
            payload = {
                "model": self.model,
                "input": text
            }
            
            # Make API request
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            # Extract embedding from response
            data = response.json()
            embedding = data['data'][0]['embedding']
            
            logger.debug(f"Generated embedding (dimension: {len(embedding)})")
            return embedding
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts at once (more efficient).
        
        Why batch?
        - OpenAI charges per API call
        - 1 call with 10 texts = cheaper than 10 calls with 1 text each
        - Faster (less overhead)
        - Better for processing chunks
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings (each is a list of 1536 floats)
        
        Example:
            texts = ["Hello", "World", "Embeddings"]
            embeddings = generator.generate_embeddings_batch(texts)
            print(len(embeddings))  # 3 embeddings
            print(len(embeddings[0]))  # 1536 dimensions
        """
        try:
            if not texts:
                logger.warning("No texts provided for embedding")
                return []
            
            logger.info(f"Generating embeddings for {len(texts)} texts")
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "input": texts
            }
            
            # Make API request
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=60  # Batch might take longer
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            # Extract embeddings from response (in same order as input)
            data = response.json()
            embeddings = [item['embedding'] for item in data['data']]
            
            logger.info(f"Successfully generated {len(embeddings)} embeddings")
            return embeddings
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
    
    def embed_chunks(self, chunks: List[dict]) -> List[dict]:
        """
        Generate embeddings for document chunks.
        
        This is the main method you'll use with DocumentProcessor output.
        
        What it does:
        1. Takes chunks from DocumentProcessor
        2. Extracts text content
        3. Generates embeddings for all at once (batch)
        4. Combines chunks with their embeddings
        5. Adds metadata
        
        Args:
            chunks: List of chunks from DocumentProcessor
                   Each chunk should have 'content' key
            
        Returns:
            List of chunks with embeddings added
        
        Example:
            from core.document_processor import DocumentProcessor
            from core.embeddings import EmbeddingGenerator
            
            processor = DocumentProcessor()
            chunks = processor.process_pdf("file.pdf")
            
            generator = EmbeddingGenerator()
            embedded_chunks = generator.embed_chunks(chunks)
            
            for chunk in embedded_chunks:
                print(f"Chunk: {chunk['content'][:50]}...")
                print(f"Embedding: {chunk['embedding'][:5]}...")  # First 5 values
        """
        try:
            # Extract just the text content from chunks
            texts = [chunk["content"] for chunk in chunks]
            
            logger.info(f"Embedding {len(texts)} chunks")
            
            # Generate embeddings for all chunks at once (efficient!)
            embeddings = self.generate_embeddings_batch(texts)
            
            # Combine chunks with their embeddings
            embedded_chunks = []
            for chunk, embedding in zip(chunks, embeddings):
                # Keep all original chunk data
                embedded_chunk = {
                    **chunk,  # Spreads all original keys (content, start_idx, end_idx)
                    "embedding": embedding,  # Add the embedding vector
                    "metadata": {
                        "type": "document_chunk",
                        "embedding_model": self.model,
                        "embedding_dimension": len(embedding)
                    }
                }
                embedded_chunks.append(embedded_chunk)
            
            logger.info(f"Successfully embedded {len(embedded_chunks)} chunks")
            return embedded_chunks
            
        except Exception as e:
            logger.error(f"Error embedding chunks: {e}")
            raise


# This runs if you run this file directly
if __name__ == "__main__":
    import logging as log_setup
    
    # Set up logging to see what's happening
    log_setup.basicConfig(
        level=log_setup.INFO,
        format='%(levelname)s - %(message)s'
    )
    
    print("\n" + "="*60)
    print("EMBEDDING GENERATOR TEST")
    print("="*60 + "\n")
    
    try:
        # Create generator
        generator = EmbeddingGenerator()
        
        # Test 1: Single embedding
        print("Test 1: Single embedding")
        text = "Machine learning is a subset of artificial intelligence"
        embedding = generator.generate_embedding(text)
        print(f"✅ Generated embedding!")
        print(f"   Dimension: {len(embedding)}")
        print(f"   First 5 values: {embedding[:5]}")
        print()
        
        # Test 2: Batch embeddings
        print("Test 2: Batch embeddings")
        texts = [
            "What is machine learning?",
            "How does neural network work?",
            "What are embeddings?"
        ]
        embeddings = generator.generate_embeddings_batch(texts)
        print(f"✅ Generated {len(embeddings)} embeddings!")
        for i, emb in enumerate(embeddings, 1):
            print(f"   Embedding {i}: {len(emb)} dimensions")
        
        print("\n" + "="*60)
        print("✅ EMBEDDING GENERATOR WORKS!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your OpenAI API key is in .env")