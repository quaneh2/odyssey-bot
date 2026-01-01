"""
RAG Engine for Ask The Odyssey application.
Handles query processing, retrieval, and response generation using Claude.
"""

import voyageai
import chromadb
from anthropic import Anthropic
import config


class OdysseyRAG:
    """
    RAG engine for querying The Odyssey.
    Uses Voyage AI for embeddings, ChromaDB for retrieval, and Claude for generation.
    """

    def __init__(self, chroma_db_path: str):
        """
        Initialize the RAG engine.

        Args:
            chroma_db_path: Path to the ChromaDB database directory
        """
        print(f"Initializing OdysseyRAG from {chroma_db_path}...")

        # Validate API keys
        if not config.VOYAGE_API_KEY:
            raise ValueError("VOYAGE_API_KEY not found in environment variables")
        if not config.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        # Initialize clients
        self.voyage_client = voyageai.Client(api_key=config.VOYAGE_API_KEY)
        self.anthropic_client = Anthropic(api_key=config.ANTHROPIC_API_KEY)

        # Load ChromaDB
        try:
            self.chroma_client = chromadb.PersistentClient(path=chroma_db_path)
            self.collection = self.chroma_client.get_collection("odyssey_chunks")
            print(f"✓ Loaded collection with {self.collection.count()} chunks")
        except Exception as e:
            raise ValueError(f"Failed to load ChromaDB: {e}")

    def _generate_query_embedding(self, query: str):
        """
        Generate embedding for the user's query.

        Args:
            query: User's question

        Returns:
            List of floats representing the query embedding
        """
        try:
            result = self.voyage_client.embed(
                [query],
                model=config.VOYAGE_MODEL,
                input_type="query"
            )
            return result.embeddings[0]
        except Exception as e:
            raise RuntimeError(f"Failed to generate query embedding: {e}")

    def _retrieve_relevant_chunks(self, query_embedding, top_k: int = None):
        """
        Retrieve most relevant chunks from the database.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to retrieve (default from config)

        Returns:
            Dictionary with ids, documents, metadatas, and distances
        """
        if top_k is None:
            top_k = config.TOP_K_RESULTS

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            return results
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve chunks: {e}")

    def _build_context(self, results):
        """
        Build context string from retrieved chunks.

        Args:
            results: Query results from ChromaDB

        Returns:
            Formatted context string
        """
        context_parts = []

        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0]

        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            book_num = metadata['book_number']
            context_parts.append(f"[Book {book_num}]\n{doc}\n")

        return "\n---\n".join(context_parts)

    def _build_prompt(self, context: str, question: str):
        """
        Build the prompt for Claude.

        Args:
            context: Retrieved context from The Odyssey
            question: User's question

        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a helpful assistant answering questions about Homer's The Odyssey.

Context from The Odyssey:
{context}

Question: {question}

Instructions:
- Answer the question based on the provided context
- Cite specific books when referencing events or characters
- If the context doesn't contain enough information, say so
- Be concise but thorough
- Use natural language, not bullet points

Answer:"""
        return prompt

    def _call_claude(self, prompt: str):
        """
        Call Claude API to generate a response.

        Args:
            prompt: The complete prompt with context and question

        Returns:
            Claude's response text
        """
        try:
            message = self.anthropic_client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=config.MAX_TOKENS,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            raise RuntimeError(f"Failed to call Claude API: {e}")

    def _format_sources(self, results):
        """
        Format retrieved sources for response.

        Args:
            results: Query results from ChromaDB

        Returns:
            List of source dictionaries
        """
        sources = []

        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0]

        for doc, metadata, distance in zip(documents, metadatas, distances):
            book_num = metadata['book_number']

            # Convert distance to a relevance score (lower distance = higher relevance)
            # Normalize to 0-1 range (this is approximate)
            relevance_score = max(0, 1 - (distance / 2))

            # Truncate text for display (first 300 characters)
            display_text = doc[:300] + "..." if len(doc) > 300 else doc

            sources.append({
                "book": f"Book {book_num}",
                "text": display_text,
                "relevance_score": round(relevance_score, 2)
            })

        return sources

    def query(self, question: str):
        """
        Process a user question and return an answer with sources.

        Args:
            question: User's question about The Odyssey

        Returns:
            Dictionary with 'answer' and 'sources' keys

        Raises:
            ValueError: If question is empty
            RuntimeError: If processing fails
        """
        # Validate input
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        question = question.strip()

        try:
            # Step 1: Generate query embedding
            query_embedding = self._generate_query_embedding(question)

            # Step 2: Retrieve relevant chunks
            results = self._retrieve_relevant_chunks(query_embedding)

            # Step 3: Build context
            context = self._build_context(results)

            # Step 4: Build prompt
            prompt = self._build_prompt(context, question)

            # Step 5: Call Claude
            answer = self._call_claude(prompt)

            # Step 6: Format sources
            sources = self._format_sources(results)

            return {
                "answer": answer,
                "sources": sources
            }

        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Query processing failed: {e}")


def test_rag_engine():
    """Test function for the RAG engine."""
    print("Testing RAG Engine...")
    print()

    try:
        # Initialize
        rag = OdysseyRAG(chroma_db_path="data/chroma_db")
        print()

        # Test query
        test_question = "Who is Odysseus?"
        print(f"Question: {test_question}")
        print()

        result = rag.query(test_question)

        print("Answer:")
        print(result['answer'])
        print()

        print("Sources:")
        for i, source in enumerate(result['sources'], 1):
            print(f"{i}. {source['book']} (relevance: {source['relevance_score']})")
            print(f"   {source['text'][:100]}...")
            print()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_rag_engine()
