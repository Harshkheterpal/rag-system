@"
# Architecture Documentation

## System Design Overview

The RAG system follows a modular, production-ready architecture with clear separation of concerns.

\`\`\`
┌─────────────────────────────────────────────────────────────┐
│                       RAG SYSTEM                             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐      ┌──────────────────┐             │
│  │  Document Layer  │      │   Query Layer    │             │
│  ├──────────────────┤      ├──────────────────┤             │
│  │ • PDF Reader     │      │ • Query Parser   │             │
│  │ • Text Extractor │      │ • Embedding Gen  │             │
│  │ • Chunker        │      │ • Search Query   │             │
│  └────────┬─────────┘      └────────┬─────────┘             │
│           │                         │                        │
│           └──────────┬──────────────┘                        │
│                      ▼                                        │
│           ┌────────────────────┐                             │
│           │  Embedding Layer   │                             │
│           ├────────────────────┤                             │
│           │ • OpenAI Embeddings│                             │
│           │ • Batch Processing │                             │
│           │ • Caching          │                             │
│           └────────┬───────────┘                             │
│                    ▼                                         │
│           ┌────────────────────┐                             │
│           │  Storage Layer     │                             │
│           ├────────────────────┤                             │
│           │ • Pinecone DB      │                             │
│           │ • Metadata Store   │                             │
│           │ • Document Index   │                             │
│           └────────┬───────────┘                             │
│                    ▼                                         │
│           ┌────────────────────┐                             │
│           │   Retrieval Layer  │                             │
│           ├────────────────────┤                             │
│           │ • Similarity Search│                             │
│           │ • Ranking          │                             │
│           │ • Context Assembly │                             │
│           └────────┬───────────┘                             │
│                    ▼                                         │
│           ┌────────────────────┐                             │
│           │   LLM Layer        │                             │
│           ├────────────────────┤                             │
│           │ • Prompt Assembly  │                             │
│           │ • GPT-4 Call       │                             │
│           │ • Response Parser  │                             │
│           └────────┬───────────┘                             │
│                    ▼                                         │
│           ┌────────────────────┐                             │
│           │   Output Layer     │                             │
│           ├────────────────────┤                             │
│           │ • Formatting       │                             │
│           │ • Source Tracking  │                             │
│           │ • Logging          │                             │
│           └────────────────────┘                             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
\`\`\`

## Component Architecture

### 1. Document Processing Layer

**File:** \`src/core/document_processor.py\`

**Responsibility:** Convert raw documents to structured chunks

**Flow:**
\`\`\`
PDF File
  ↓
PyPDF2 Reader
  ↓
Text Extraction (per page)
  ↓
Cleaning (remove extra whitespace)
  ↓
Chunking (500 char chunks, 50 char overlap)
  ↓
Chunk Objects with Metadata
\`\`\`

**Key Design Decisions:**
- Chunk size: 500 characters (~300 words)
  - Large enough for context
  - Small enough for LLM token limits
- Overlap: 50 characters
  - Prevents losing info at chunk boundaries
  - Maintains sentence continuity
- Error handling: Graceful failures
  - Corrupted PDFs don't crash system
  - Logging for debugging

### 2. Embedding Layer

**File:** \`src/core/embeddings.py\`

**Responsibility:** Convert text to vector representations

**Why Ada Model (not GPT-4)?**
- Cost: \$0.02 per 1M tokens (vs \$0.03 for GPT-4)
- Speed: Instant responses
- Dimensionality: 1536 dimensions (good balance)
- Performance: Excellent for semantic search

**Flow:**
\`\`\`
Text Chunks
  ↓
Batch Processing (10 chunks per API call)
  ↓
OpenAI Ada Embedding API
  ↓
1536-dimensional vectors
  ↓
Add Metadata
  ↓
Ready for Storage
\`\`\`

**Optimization Strategies:**
- Batch processing: Reduces API calls by 90%
- Caching: Store embeddings to avoid re-computing
- Async calls: Process multiple batches in parallel

### 3. Vector Storage Layer

**File:** \`src/core/vector_store.py\`

**Responsibility:** Store and retrieve embeddings efficiently

**Why Pinecone?**
- Millisecond retrieval (even with millions of vectors)
- Serverless (no infrastructure management)
- Metadata filtering (find chunks by source, date, etc.)
- Auto-scaling (handles traffic spikes)

**Storage Structure:**
\`\`\`
Vector ID: "doc-1-chunk-5"
Vector: [0.21, -0.45, 0.89, ..., 0.12]  (1536 dimensions)
Metadata: {
  "content": "First 500 chars of chunk...",
  "source": "report.pdf",
  "chunk_index": 5,
  "page": 2
}
\`\`\`

**Retrieval Strategy:**
- Cosine similarity (most documents use this)
- Top-K retrieval (get 3-5 most similar chunks)
- Score filtering (only chunks above 0.7 similarity)

### 4. RAG Chain Layer

**File:** \`src/core/rag_chain.py\`

**Responsibility:** Orchestrate retrieval + LLM answering

**Flow:**
\`\`\`
User Question
  ↓
Embed Question (same Ada model)
  ↓
Search Pinecone (find similar chunks)
  ↓
Retrieve Top 3 Chunks
  ↓
Build Prompt with Context
  ↓
Call GPT-4 with Instructions
  ↓
Parse Response
  ↓
Return Answer + Source Chunks
\`\`\`

**Prompt Engineering:**
\`\`\`
System: "Answer only based on provided chunks. 
         If info not in chunks, say so. 
         Never make up information."

Chunks:
[Chunk 1]
[Chunk 2]
[Chunk 3]

Question: [User's question]
\`\`\`

**Why This Prevents Hallucinations:**
1. System prompt sets expectations
2. Only relevant chunks provided (no false memories)
3. GPT-4 instructed to refuse out-of-context questions
4. Logging tracks when model makes errors

### 5. API Layer

**File:** \`src/api/main.py\`

**Responsibility:** Expose RAG system via REST API

**Endpoints:**

\`POST /upload\`
- Accept PDF file
- Process document
- Return: document_id, chunk_count

\`POST /ask\`
- Accept: document_id, question
- Retrieve answer
- Return: answer, source_chunks, metadata

\`GET /health\`
- Simple health check
- Return: {"status": "healthy"}

**Error Handling:**
- Invalid file type → 400 Bad Request
- Large file → 413 Payload Too Large
- API timeout → 504 Gateway Timeout
- Graceful degradation

## Data Flow Examples

### Example 1: Upload Document

\`\`\`
1. User uploads research.pdf
2. DocumentProcessor extracts text
   - 50 pages → 25,000 words
3. Creates 50 chunks (500 words each)
4. EmbeddingGenerator creates embeddings
   - Batch: [chunk1, chunk2, chunk3, ...]
   - OpenAI API call
   - Returns: [vector1, vector2, vector3, ...]
5. VectorStore stores in Pinecone
   - research-1, research-2, ..., research-50
6. Return: "Successfully uploaded 50 chunks"
\`\`\`

### Example 2: Answer Question

\`\`\`
1. User asks: "What are the key findings?"
2. Embed question: "What are the key findings?" → vector_q
3. Search Pinecone: Find similar vectors
   - Similarity scores: [0.92, 0.88, 0.84, ...]
   - Top 3: chunks 15, 8, 42
4. Retrieve chunks:
   - Chunk 15: "Main finding: X is Y"
   - Chunk 8: "Finding 2: A is B"
   - Chunk 42: "Finding 3: P is Q"
5. Build prompt with chunks + question
6. Call GPT-4 with context
7. Response: "Key findings are X, A, and P..."
8. Return: Answer + source chunks
\`\`\`

## Performance Considerations

### Latency Breakdown (per request)

| Component | Time | Notes |
|-----------|------|-------|
| Embedding question | 200ms | OpenAI API |
| Pinecone search | 50ms | Vector DB |
| LLM API call | 1500ms | GPT-4 generation |
| Network overhead | 250ms | Totals |
| **Total** | **~2s** | Target: <3s |

### Cost Breakdown (per 1000 requests)

| Component | Cost | Notes |
|-----------|------|-------|
| Ada Embeddings | \$0.01 | 100K tokens |
| GPT-4 | \$3.00 | 100K tokens (input/output) |
| Pinecone | \$0.20 | Free tier up to 100K vectors |
| **Total** | **\$3.21** | Per 1000 questions |

### Scaling Strategy

- **Document Level:** Can handle millions of documents
- **Query Level:** Can handle 1000s of concurrent queries
- **Cost Level:** Stays \$3-5 per 1000 queries at scale

## Security Considerations

### API Key Management
- .env file (never committed)
- Environment variables (production)
- No hardcoded secrets
- Regular key rotation

### Input Validation
- File size limits (max 50MB)
- File type validation (PDF only)
- Question length limits (prevent abuse)
- Rate limiting (prevent DoS)

### Data Privacy
- No storage of user questions
- No caching of sensitive data
- PDFs processed in memory
- Logs don't contain sensitive info

## Error Handling Strategy

\`\`\`python
try:
    # Main operation
    result = process_pdf(file)
except FileNotFoundError:
    # Specific error
    logger.error("PDF not found")
    return {"error": "File not found"}
except Exception as e:
    # Catch-all
    logger.error(f"Unexpected error: {e}")
    return {"error": "Internal server error"}
\`\`\`

## Testing Strategy

### Unit Tests
- Test each component independently
- Mock external APIs (OpenAI, Pinecone)
- Test edge cases (empty PDF, large file, etc.)
- Target: 80%+ coverage

### Integration Tests
- Test full pipeline
- Use real PDFs
- Verify end-to-end accuracy
- Test error scenarios

### Load Tests
- Test concurrent requests
- Verify latency under load
- Check cost efficiency
- Identify bottlenecks

## Future Architectural Improvements

1. **Caching Layer**
   - Cache embeddings to save money
   - Cache LLM responses for common questions
   - Reduce latency

2. **Async Processing**
   - Queue documents for processing
   - Process in background
   - Return results via webhook

3. **Multi-Model Support**
   - Support Claude, Llama, etc.
   - Route based on question type
   - A/B testing

4. **Conversation Memory**
   - Track conversation history
   - Multi-turn context
   - Personalization

5. **Analytics**
   - Track accuracy
   - Monitor costs
   - Usage patterns
   - Performance metrics

---

**Last Updated:** $(Get-Date -Format 'MMMM dd, yyyy')
"@ | Out-File -Encoding UTF8 "docs/ARCHITECTURE.md"
