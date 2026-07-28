# System Architecture

## Overview

RAG system that combines document retrieval with LLM generation for accurate Q&A.

## Components

### 1. Document Processor

Reads PDFs and breaks them into chunks.

Input: PDF file
Output: List of text chunks with metadata

Key decisions:
- Chunk size: 500 characters
- Overlap: 50 characters (maintain context)
- Technology: PyPDF2

### 2. Embeddings Generator

Converts text chunks to vector representations.

Input: Text chunks
Output: Vectors (1536 dimensions)

Technology: OpenAI text-embedding-3-small (Ada)
Cost: ~$0.02 per 1M tokens

Why Ada and not other models:
- Cheap ($0.02 vs $0.10 per 1M for GPT)
- Fast (instant)
- Good quality for search

### 3. Vector Store

Stores embeddings for fast retrieval.

Input: Embeddings + metadata
Output: Similarity search results

Technology: Pinecone
Why Pinecone:
- Free tier (generous)
- Serverless (no setup)
- Automatic scaling
- Fast similarity search

### 4. RAG Chain

Orchestrates retrieval + generation.

Process:
1. User asks question
2. Convert question to embedding
3. Search vector store for similar chunks
4. Take top 3 most similar chunks
5. Send chunks + question to GPT-4
6. GPT-4 generates answer based on chunks
7. Return answer to user

Technology: LangChain + OpenAI GPT-4

### 5. API Layer

REST endpoints for client access.

Endpoints (planned):
- POST /upload - Upload PDF
- POST /query - Ask question
- GET /health - System status

Technology: FastAPI

### 6. Frontend

User interface for uploading and querying.

Technology: Streamlit (simple) or HTML/React (advanced)

## Data Flow

PDF Upload
|
v
Document Processor (extract text, chunk)
|
v
Embeddings Generator (Ada model)
|
v
Vector Store (Pinecone)
|
v
User Question
|
v
Embeddings Generator (embed question)
|
v
Vector Store (retrieve top 3 chunks)
|
v
RAG Chain (send to GPT-4)
|
v
GPT-4 LLM (generate answer)
|
v
Answer to User

## Design Decisions

### Why Chunking?

GPT-4 has token limits (~8000). A 50-page PDF is ~15k tokens. 
Splitting into 500-char chunks (~250 tokens each) lets us:
- Stay under token limits
- Send only relevant context
- Reduce API costs

### Why Embeddings?

Need fast similarity search across thousands of chunks.
Embeddings allow vector-based search which is O(1) with Pinecone.

### Why Not RAG?

Traditional approach: Fine-tune GPT on your documents.
Problems:
- Expensive ($$$)
- Takes time
- Hard to update docs
- Risk of hallucinations

RAG is better because:
- Cheap (just API calls)
- Always up-to-date
- Grounded in actual documents
- Solves hallucination problem

## Error Handling

What could go wrong:

1. Bad PDF
   - Handle: Try/catch, log error, return friendly message

2. API timeout
   - Handle: Retry logic (max 3 times), fallback message

3. Large PDF (>50MB)
   - Handle: Reject with message, suggest chunking first

4. Empty document
   - Handle: Detect, ask user for valid PDF

5. Pinecone down
   - Handle: Graceful degradation, queue requests

## Performance Targets

- Response time: <3 seconds (p95)
- Chunk retrieval: <100ms
- Embedding generation: <500ms
- LLM answer: <2 seconds

## Scalability

Current design handles:
- 50-100 documents
- 100-1000 chunks
- 10 concurrent users

To scale to millions:
- Add caching layer (Redis)
- Async processing (Celery)
- Multiple API instances
- Load balancer
