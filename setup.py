"""
Setup script for Ask The Odyssey RAG application.
Downloads The Odyssey, processes it, generates embeddings, and creates the vector database.
This script should be run once before starting the application.
"""

import os
import re
import time
import requests
import voyageai
import chromadb
from chromadb.config import Settings
import config

# Constants
GUTENBERG_URL = "https://www.gutenberg.org/files/1727/1727-0.txt"
DATA_DIR = "data"
ODYSSEY_FILE = os.path.join(DATA_DIR, "odyssey.txt")
CHROMA_DB_DIR = os.path.join(DATA_DIR, "chroma_db")


def download_odyssey():
    """Download The Odyssey from Project Gutenberg."""
    print("Downloading The Odyssey from Project Gutenberg...")

    try:
        response = requests.get(GUTENBERG_URL, timeout=30)
        response.raise_for_status()

        with open(ODYSSEY_FILE, 'w', encoding='utf-8') as f:
            f.write(response.text)

        print(f"✓ Successfully downloaded to {ODYSSEY_FILE}")
        return response.text
    except Exception as e:
        print(f"✗ Error downloading The Odyssey: {e}")
        raise


def preprocess_text(text):
    """
    Remove Project Gutenberg header/footer and clean the text.
    Extract only The Odyssey content.
    """
    print("Preprocessing text...")

    # Find the start of Book I
    start_patterns = [
        r"BOOK I",
        r"Book I",
        r"\*\*\* START OF THE PROJECT GUTENBERG EBOOK"
    ]

    start_idx = 0
    for pattern in start_patterns:
        match = re.search(pattern, text)
        if match:
            start_idx = match.start()
            # If it's the Gutenberg marker, find the actual Book I after it
            if "GUTENBERG" in match.group():
                book_match = re.search(r"BOOK I", text[start_idx:])
                if book_match:
                    start_idx = start_idx + book_match.start()
            break

    # Find the end (before Project Gutenberg footer)
    end_patterns = [
        r"\*\*\* END OF THE PROJECT GUTENBERG EBOOK",
        r"End of.*Project Gutenberg",
        r"THE END"
    ]

    end_idx = len(text)
    for pattern in end_patterns:
        match = re.search(pattern, text[start_idx:])
        if match:
            end_idx = start_idx + match.start()
            break

    # Extract the main content
    cleaned_text = text[start_idx:end_idx]

    # Clean up extra whitespace
    cleaned_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_text)  # Multiple blank lines to double
    cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)  # Multiple spaces to single

    print(f"✓ Preprocessed text ({len(cleaned_text)} characters)")
    return cleaned_text


def parse_books(text):
    """
    Parse the text into books (I through XXIV).
    Returns a list of dictionaries with book metadata.
    """
    print("Parsing book structure...")

    # Find all book markers
    book_pattern = r'BOOK\s+([IVX]+)'
    matches = list(re.finditer(book_pattern, text, re.IGNORECASE))

    books = []
    for i, match in enumerate(matches):
        book_num = match.group(1).upper()
        start_pos = match.start()

        # End is the start of the next book, or end of text
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        book_text = text[start_pos:end_pos]
        books.append({
            'number': book_num,
            'text': book_text.strip(),
            'start': start_pos,
            'end': end_pos
        })

    print(f"✓ Found {len(books)} books")
    return books


def estimate_tokens(text):
    """Rough estimation: 1 token ≈ 4 characters."""
    return len(text) // 4


def chunk_text(books):
    """
    Split books into chunks with overlap.
    Each chunk is roughly CHUNK_SIZE tokens with CHUNK_OVERLAP tokens of overlap.
    """
    print(f"Chunking text (chunk_size={config.CHUNK_SIZE}, overlap={config.CHUNK_OVERLAP})...")

    chunks = []
    chunk_id = 0

    for book in books:
        book_text = book['text']
        book_num = book['number']

        # Split by paragraphs first to avoid breaking mid-paragraph
        paragraphs = book_text.split('\n\n')

        current_chunk = ""
        current_tokens = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_tokens = estimate_tokens(para)

            # If adding this paragraph would exceed chunk size
            if current_tokens + para_tokens > config.CHUNK_SIZE and current_chunk:
                # Save current chunk
                chunks.append({
                    'id': f'chunk_{chunk_id}',
                    'text': current_chunk.strip(),
                    'book_number': book_num,
                    'chunk_index': chunk_id
                })
                chunk_id += 1

                # Start new chunk with overlap
                # Take last CHUNK_OVERLAP tokens from current chunk
                overlap_chars = config.CHUNK_OVERLAP * 4
                current_chunk = current_chunk[-overlap_chars:] + '\n\n' + para
                current_tokens = estimate_tokens(current_chunk)
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += '\n\n' + para
                else:
                    current_chunk = para
                current_tokens += para_tokens

        # Save remaining chunk
        if current_chunk.strip():
            chunks.append({
                'id': f'chunk_{chunk_id}',
                'text': current_chunk.strip(),
                'book_number': book_num,
                'chunk_index': chunk_id
            })
            chunk_id += 1

    print(f"✓ Created {len(chunks)} chunks")
    return chunks


def generate_embeddings(chunks):
    """Generate embeddings for all chunks using Voyage AI."""
    print(f"Generating embeddings using {config.VOYAGE_MODEL}...")

    if not config.VOYAGE_API_KEY:
        raise ValueError("VOYAGE_API_KEY not found in environment variables")

    try:
        vo = voyageai.Client(api_key=config.VOYAGE_API_KEY)

        # Extract texts for embedding
        texts = [chunk['text'] for chunk in chunks]

        # Voyage AI supports batch embedding - process in batches of 128
        batch_size = 128
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            print(f"  Processing batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}...")

            result = vo.embed(
                batch_texts,
                model=config.VOYAGE_MODEL,
                input_type="document"
            )

            all_embeddings.extend(result.embeddings)

            # Rate limiting - be respectful
            if i + batch_size < len(texts):
                time.sleep(1)

        print(f"✓ Generated {len(all_embeddings)} embeddings")
        return all_embeddings

    except Exception as e:
        print(f"✗ Error generating embeddings: {e}")
        raise


def create_vector_database(chunks, embeddings):
    """Create ChromaDB database with chunks and embeddings."""
    print("Creating ChromaDB vector database...")

    try:
        # Initialize ChromaDB with persistent storage
        client = chromadb.PersistentClient(path=CHROMA_DB_DIR)

        # Delete collection if it exists (for clean setup)
        try:
            client.delete_collection("odyssey_chunks")
        except:
            pass

        # Create new collection
        collection = client.create_collection(
            name="odyssey_chunks",
            metadata={"description": "Chunks from Homer's The Odyssey"}
        )

        # Prepare data for insertion
        ids = [chunk['id'] for chunk in chunks]
        documents = [chunk['text'] for chunk in chunks]
        metadatas = [
            {
                'book_number': chunk['book_number'],
                'chunk_index': chunk['chunk_index']
            }
            for chunk in chunks
        ]

        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            end_idx = min(i + batch_size, len(chunks))

            collection.add(
                ids=ids[i:end_idx],
                embeddings=embeddings[i:end_idx],
                documents=documents[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )

            print(f"  Added {end_idx}/{len(chunks)} chunks...")

        print(f"✓ Database created at {CHROMA_DB_DIR}")
        print(f"  Collection: odyssey_chunks")
        print(f"  Total chunks: {collection.count()}")

        return collection

    except Exception as e:
        print(f"✗ Error creating database: {e}")
        raise


def main():
    """Main setup function."""
    print("=" * 60)
    print("Ask The Odyssey - Setup Script")
    print("=" * 60)
    print()

    # Create data directory if it doesn't exist
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"✓ Created {DATA_DIR} directory")

    # Download The Odyssey
    if os.path.exists(ODYSSEY_FILE):
        print(f"The Odyssey already downloaded at {ODYSSEY_FILE}")
        with open(ODYSSEY_FILE, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = download_odyssey()

    print()

    # Preprocess
    cleaned_text = preprocess_text(text)
    print()

    # Parse books
    books = parse_books(cleaned_text)
    print()

    # Chunk text
    chunks = chunk_text(books)
    print()

    # Generate embeddings
    embeddings = generate_embeddings(chunks)
    print()

    # Create database
    collection = create_vector_database(chunks, embeddings)
    print()

    # Summary
    print("=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print(f"Total books processed: {len(books)}")
    print(f"Total chunks created: {len(chunks)}")
    print(f"Database location: {CHROMA_DB_DIR}")
    print()
    print("You can now run the application with: python app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
