# Ask The Odyssey

A web-based Retrieval-Augmented Generation (RAG) application that allows users to ask questions about Homer's *The Odyssey* and receive accurate, AI-powered answers with citations from the original text.

**[Try the live demo](https://odyssey-bot-r0p3.onrender.com/)**

## Overview

Ask The Odyssey combines modern AI technologies to create an interactive experience with classical literature. Users can ask natural language questions about characters, events, and themes in *The Odyssey*, and receive contextual answers backed by relevant passages from the epic.

## Technologies Used

- **Python 3.9+** - Core programming language
- **Flask** - Web framework for the application server
- **Anthropic Claude** - Large language model for generating responses (claude-sonnet-4-20250514)
- **Voyage AI** - Embedding generation for semantic search (voyage-3)
- **ChromaDB** - Vector database for storing and retrieving text embeddings
- **HTML/CSS/JavaScript** - Frontend interface

## Features

- **Natural Language Q&A**: Ask questions in plain English about any aspect of The Odyssey
- **Source Citations**: Every answer includes relevant passages from the text with book references
- **Relevance Scoring**: See how relevant each source passage is to your question
- **Example Questions**: Quick-start with pre-written example questions
- **Clean UI**: Classical, literature-inspired design with responsive layout
- **Fast Semantic Search**: Vector-based retrieval finds the most relevant context in milliseconds

## Prerequisites

Before you begin, ensure you have:

- Python 3.9 or higher installed
- An [Anthropic API key](https://console.anthropic.com/) (for Claude)
- A [Voyage AI API key](https://www.voyageai.com/) (for embeddings)

## Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd odyssey-bot
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv

   # On macOS/Linux:
   source venv/bin/activate

   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and add your API keys
   # ANTHROPIC_API_KEY=your_anthropic_api_key_here
   # VOYAGE_API_KEY=your_voyage_api_key_here
   ```

## Setup

Before running the application for the first time, you need to download *The Odyssey* and create the vector database:

```bash
python setup.py
```

This one-time setup script will:
1. Download *The Odyssey* from Project Gutenberg
2. Preprocess and clean the text
3. Split the text into manageable chunks
4. Generate embeddings for each chunk using Voyage AI
5. Create a ChromaDB vector database

**Note**: This process may take 5-10 minutes depending on your internet connection and API rate limits.

## Usage

Once setup is complete, start the application:

```bash
python app.py
```

Then open your web browser and navigate to:
```
http://localhost:5000
```

### Asking Questions

1. Type your question in the text area
2. Click "Ask Question" or press Ctrl+Enter (Cmd+Enter on Mac)
3. Wait for the AI to process your question (usually 2-5 seconds)
4. View the answer and relevant source passages

### Example Questions

- What happened to Odysseus's crew?
- Who is Circe and what role does she play?
- Describe Odysseus's encounter with the Cyclops
- What is Penelope doing while Odysseus is away?
- How does The Odyssey end?

## Project Structure

```
odyssey-bot/
├── setup.py                 # One-time setup script
├── app.py                   # Flask application server
├── rag_engine.py           # RAG query processing logic
├── config.py               # Configuration and settings
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment variables
├── .gitignore             # Git ignore file
├── README.md              # This file
├── static/
│   ├── style.css          # Frontend styling
│   └── script.js          # Frontend JavaScript
├── templates/
│   └── index.html         # Main page template
└── data/
    ├── odyssey.txt        # Source text (created by setup)
    └── chroma_db/         # Vector database (created by setup)
```

## How It Works

Ask The Odyssey uses a RAG (Retrieval-Augmented Generation) architecture:

1. **Indexing Phase** (setup.py):
   - Downloads The Odyssey from Project Gutenberg
   - Splits the text into overlapping chunks (~800 tokens each)
   - Generates vector embeddings for each chunk using Voyage AI
   - Stores chunks and embeddings in ChromaDB

2. **Query Phase** (when you ask a question):
   - Your question is converted to a vector embedding
   - ChromaDB performs semantic search to find the most relevant text chunks
   - The top 5 most relevant chunks are retrieved
   - These chunks are provided as context to Claude
   - Claude generates an answer based on the context
   - The answer and source passages are displayed

### Why RAG?

Traditional LLMs can't access specific text content beyond their training data. RAG solves this by:
- Providing relevant context from the actual source text
- Ensuring answers are grounded in the original material
- Enabling citation of specific passages
- Reducing hallucinations and improving accuracy

## API Keys

### Getting an Anthropic API Key

1. Visit [console.anthropic.com](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy it to your `.env` file

### Getting a Voyage AI API Key

1. Visit [voyageai.com](https://www.voyageai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy it to your `.env` file

## Configuration

You can customize the application behavior by editing [config.py](config.py):

- `CHUNK_SIZE`: Size of text chunks (default: 800 tokens)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 100 tokens)
- `TOP_K_RESULTS`: Number of chunks to retrieve (default: 5)
- `MAX_TOKENS`: Maximum response length (default: 2000)

## Troubleshooting

### "Database not found" error
- Make sure you've run `python setup.py` first
- Check that `data/chroma_db/` directory exists

### API errors
- Verify your API keys are correctly set in `.env`
- Check you have sufficient API credits
- Ensure you have internet connectivity

### Setup script fails
- Check your internet connection
- Verify API keys are valid
- Try running setup again (it will resume where it left off)

## Future Enhancements

Possible improvements for this project:

- **Conversation History**: Track previous questions and answers
- **Book Filtering**: Allow users to search specific books only
- **Text Highlighting**: Highlight specific relevant phrases in sources
- **Export Functionality**: Download answers as PDF
- **Dark Mode**: Toggle between light and dark themes
- **Advanced Search**: Filter by character, theme, or book
- **Analytics Dashboard**: Track popular questions and usage patterns
- **Multi-language Support**: Support questions in multiple languages

## Contributing

Contributions are welcome! Areas for improvement:

- Better chunking strategies
- Enhanced UI/UX design
- Additional error handling
- Performance optimizations
- Test coverage

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Acknowledgments

- **Project Gutenberg** for providing free access to *The Odyssey*
- **Anthropic** for Claude AI
- **Voyage AI** for embeddings
- **ChromaDB** for vector storage
- Homer for writing *The Odyssey* approximately 2,700 years ago

## Contact & Support

For questions, issues, or suggestions:
- Open an issue in the repository
- Check existing documentation
- Review the troubleshooting section

---

Built with modern AI to explore ancient literature.
