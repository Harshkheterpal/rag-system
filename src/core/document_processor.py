"""
Document Processing Module
Handles PDF reading, text extraction, and chunking

What this does:
1. Reads PDF files (extracts all text)
2. Breaks text into chunks (500 chars each)
3. Overlaps chunks (50 chars repeat) to maintain context
4. Returns structured chunks with metadata

Why this is needed:
- LLMs have token limits (~8000 for GPT-4)
- A 50-page PDF is ~15,000 tokens (too big!)
- Split into chunks so we can send only relevant ones to LLM
- Overlap prevents losing context at chunk boundaries
"""

import logging
from typing import List, Dict
from pathlib import Path

# PyPDF2 is what reads PDFs
try:
    from PyPDF2 import PdfReader
except ImportError:
    print("ERROR: PyPDF2 not installed. Run: pip install PyPDF2")
    exit(1)

# Set up logging (so we can see what's happening)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Processes documents (PDF) and converts them into chunks.
    
    Example:
        processor = DocumentProcessor(chunk_size=500, overlap=50)
        chunks = processor.process_pdf("myfile.pdf")
        print(f"Created {len(chunks)} chunks")
    """
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        Initialize the document processor.
        
        Args:
            chunk_size: Number of characters per chunk (default 500)
            overlap: Characters to repeat between chunks (default 50)
        
        Example:
            processor = DocumentProcessor(chunk_size=500, overlap=50)
            # This creates 500-char chunks with 50-char overlap
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        logger.info(f"DocumentProcessor initialized: chunk_size={chunk_size}, overlap={overlap}")
    
    def read_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            All text from the PDF as one big string
            
        Raises:
            FileNotFoundError: If PDF doesn't exist
            ValueError: If PDF is corrupted or can't be read
        
        Example:
            text = processor.read_pdf("document.pdf")
            print(text)  # All text from the PDF
        """
        try:
            # Convert path to Path object (handles \ vs / automatically)
            path = Path(pdf_path)
            
            # Check if file exists
            if not path.exists():
                raise FileNotFoundError(f"PDF not found: {pdf_path}")
            
            # Read PDF
            logger.info(f"Reading PDF: {pdf_path}")
            text = ""
            
            # Open and read PDF file
            with open(pdf_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                num_pages = len(pdf_reader.pages)
                logger.info(f"PDF has {num_pages} pages")
                
                # Extract text from each page
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        text += page_text + "\n"
                        logger.debug(f"Extracted page {page_num + 1}/{num_pages}")
                    except Exception as e:
                        logger.warning(f"Could not extract text from page {page_num + 1}: {e}")
                        continue
            
            # Verify we got text
            if not text.strip():
                raise ValueError("PDF appears to be empty or unreadable")
            
            logger.info(f"Successfully extracted {len(text)} characters from PDF")
            return text
            
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            raise ValueError(f"Failed to read PDF: {str(e)}")
    
    def chunk_text(self, text: str) -> List[Dict[str, any]]:
        chunks = []
        start = 0  # Where we start reading
        
        # Keep chunking until we reach the end of text
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # Don't go past the end
            if end > len(text):
                end = len(text)
            
            # Extract the chunk
            chunk_text = text[start:end].strip()
            
            # Only add non-empty chunks
            if chunk_text:
                chunks.append({
                    "content": chunk_text,
                    "start_idx": start,
                    "end_idx": end
                })
            
            # Move start for next chunk (overlap makes sure we don't lose context)
            # If overlap=50 and chunk_size=500, we move 450 (500-50)
            new_start = end - self.overlap
            
            # IMPORTANT: Prevent infinite loop
            # If new_start didn't move us forward significantly, jump to end
            if new_start >= end:
                break
            
            # If we're at the end, stop
            if end >= len(text):
                break
            
            start = new_start
        
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
    
    def process_pdf(self, pdf_path: str) -> List[Dict[str, any]]:
        """
        Main method: Read PDF and return chunks.
        
        This is what you call to process a PDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of text chunks ready for embedding
        
        Example:
            processor = DocumentProcessor()
            chunks = processor.process_pdf("research_paper.pdf")
            
            for chunk in chunks:
                print(chunk['content'][:50])  # Print first 50 chars
        """
        logger.info(f"Processing PDF: {pdf_path}")
        
        # Step 1: Read the PDF
        text = self.read_pdf(pdf_path)
        
        # Step 2: Split into chunks
        chunks = self.chunk_text(text)
        
        logger.info(f"PDF processing complete: {len(chunks)} chunks")
        return chunks


# This runs if you run this file directly (not imported)
if __name__ == "__main__":
    # Set up logging to see what's happening
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*60)
    print("DOCUMENT PROCESSOR TEST")
    print("="*60 + "\n")
    
    # Create processor
    processor = DocumentProcessor(chunk_size=500, overlap=50)
    
    # Test with a PDF
    # (You'll need to have a PDF file in your project folder)
    # For now, this just shows how to use it
    
    print("✅ Document processor ready!")
    print("To use it:")
    print("  processor = DocumentProcessor()")
    print("  chunks = processor.process_pdf('your_file.pdf')")
    print("  print(f'Created {len(chunks)} chunks')")
    print("\n" + "="*60 + "\n")