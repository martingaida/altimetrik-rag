# Salesforce Earnings Call RAG System

A Retrieval-Augmented Generation (RAG) system designed to analyze and answer questions about Salesforce earnings call transcripts. The system uses advanced NLP techniques, including query expansion and semantic search, to provide accurate answers from the earnings call documents.

## Features

- 🔍 Semantic search with query expansion
- 💡 Context-aware answer generation
- 🤖 Interactive chatbot interface
- 📊 Metadata-aware document retrieval
- 🎯 Specialized for financial earnings calls

## Architecture

### Overview

The system follows a modular RAG architecture with the following main components:

1. **Data Pipeline**
   - Document ingestion and preprocessing
   - Chunking and metadata extraction
   - Vector embedding generation
   - Storage in MongoDB (raw data) and Qdrant (vector store)

2. **Retrieval Pipeline**
   - Query expansion for better semantic coverage
   - Self-query mechanism for metadata extraction
   - Semantic search using Qdrant
   - Context reranking for relevance

3. **Inference Pipeline**
   - Context preparation and aggregation
   - LLM-based answer generation
   - Response formatting and validation

4. **Interface Layer**
   - FastAPI backend service
   - Streamlit chat interface
   - REST API endpoints

### Technical Components

#### Query Processing
- **Query Expansion**: Uses LangChain and OpenAI to generate semantically similar queries
- **Self Query**: Extracts key terms and metadata using specialized prompts
- **Metadata Handling**: Processes document metadata for enhanced retrieval

#### Retrieval System
- **Vector Store**: Qdrant for efficient similarity search
- **Raw Storage**: MongoDB for document storage and metadata
- **Reranking**: Custom reranking logic for result relevance

#### Answer Generation
- **Context Preparation**: Formats retrieved documents for LLM consumption
- **LLM Integration**: OpenAI API integration with customizable prompts
- **Response Validation**: Answer quality checks and error handling

### Data Flow

1. **User Input**
   ```
   Query → Query Expansion → Self Query → Metadata Extraction
   ```

2. **Retrieval**
   ```
   Expanded Queries → Vector Search → Reranking → Context Assembly
   ```

3. **Generation**
   ```
   Context + Query → LLM Processing → Answer Generation → Response Formatting
   ```

## Setup

### Prerequisites

#### Local Dependencies
- Python 3.11
- Pyenv >=2.3.36 (optional: for installing multiple Python versions on your machine)
- Poetry >=1.8.3
- Docker >=27.1.1
- aws CLI >=2.15.42
- git >=2.44.0

#### Cloud Dependencies
- MongoDB (NoSQL database)
- Qdrant (vector database)
- OpenAI API key
- ZenML (for pipeline orchestration)
- AWS (for external stack hosting)

### Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/martingaida/altimetrik-rag.git
cd altimetrik-rag
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
poetry install
```

4. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
OPENAI_API_KEY=your_api_key
MONGODB_URI=your_mongodb_uri
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
OPENAI_MODEL=gpt-4-1106-preview
VECTOR_COLLECTION_NAME=your_collection_name
```

## Running the System

1. Start the FastAPI backend:
```bash
uvicorn steps.inference_api:app --reload --port 8000
```

2. In a separate terminal, start the Streamlit interface:
```bash
streamlit run interface/streamlit_app.py
```

3. Access the chat interface at `http://localhost:8501`

### RAG Endpoint

```bash
POST /rag
Content-Type: application/json

{
    "query": "What was Salesforce's revenue guidance for next quarter?"
}
```

Response:
```json
{
    "answer": "Based on the earnings call transcript..."
}
```

### Example Queries

The system is optimized for questions like:
- "When was the most recent earnings call?"
- "What are the risks that Salesforce has faced?"
- "Can you summarize Salesforce's strategy at the beginning of 2023?"
- "How many earnings call documents do you have indexed?"
- "How many pages are in the most recent earnings call?"

## Development

### Project Structure

```
salesforce-rag/
├── infrastructure/             # Infrastructure components
│   └── db/                     # Database clients
├── interface/
│   └── streamlit_app.py        # Streamlit chat interface
├── model/
│   └── inference/              # LLM interaction logic
│       └── inference.py        # Core inference implementation
├── pipelines/
│   ├── etl.py                  # ETL pipeline (lines 1-34)
│   ├── ingestion.py            # Data ingestion pipeline
│   ├── inference.py            # Inference pipeline
│   └── retrieval.py            # Retrieval pipeline
├── steps/
│   ├── etl/                    # ETL processing steps
│   │   ├── clean.py            # Text cleaning
│   │   ├── normalize.py        # Text normalization
│   │   └── transform.py        # Data transformation
│   ├── ingestion/              # Data ingestion steps
│   │   ├── chunk_embed.py      # Chunking & embedding
│   │   ├── clean.py              # Document cleaning
│   │   ├── load_to_vector_db.py  # Vector DB loading
│   │   └── query_data_warehouse.py # Data querying
│   ├── inference/                  # Inference steps
│   │   ├── context.py          # Context preparation
│   │   └── api.py              # FastAPI endpoints
│   ├── retrieval/              # Retrieval steps
│   │   ├── query_expansion.py  # Query expansion
│   │   ├── reranking.py        # Result reranking
│   │   └── self_query.py       # Self-query generation
│   └── prompt_templates.py     # LLM prompts
├── tests/                    # Test suite
│   ├── run_rag.py            # RAG End-to-End test
│   └── run_retrieval.py      # Retrieval Pipeline test
└── shared/
    ├── domain/                 # Domain models
    │   ├── base/
    │   │   └── vector.py       # Base vector operations
    │   ├── embedded_chunks.py  # Embedded chunk models
    │   └── exceptions.py       # Custom exceptions
    ├── preprocessing/          # Preprocessing components
    │   ├── operations/         # Core operations
    │   │   ├── chunking.py     # Text chunking
    │   │   └── cleaning.py     # Text cleaning
    │   ├── chunking_data_handlers.py   # Chunk processing
    │   ├── cleaning_data_handlers.py   # Clean processing
    │   ├── embedding_data_handlers.py  # Embedding processing
    │   └── dispatchers.py              # Operation dispatchers
    └── utils/                  # Shared utilities
        └── misc.py             # Miscellaneous helpers
```

### Monitoring and Logging

The system uses `loguru` for comprehensive logging:
- API requests and responses
- Pipeline execution steps
- Error tracking and debugging
- Performance metrics

### Performance Optimization

- Query expansion is limited to 3 variations for balance
- Context window optimized for relevant information
- Batch processing for efficient vector search

## Testing

### Manual Testing Tools

1. **RAG Testing** (`run_rag.py`)
   - Tests complete RAG pipeline through API endpoint
   - Example usage:
   ```python
   from tools.run_rag import test_simple_rag
   
   query = "Can you summarize Salesforce's strategy at the beginning of 2023?"
   answer = test_simple_rag(query)
   ```

2. **Retrieval Testing** (`run_retrieval.py`)
   - Tests context retrieval functionality
   - Example usage:
   ```python
   from tools.run_retrieval import test_retrieval
   
   test_retrieval()
   ```