# KNAI - Natural Language Data Analytics Platform

## About The Project
KNAI is an advanced AI-powered platform that revolutionizes data analysis by enabling natural language interactions with structured databases. Our solution transforms everyday language questions into optimized SQL queries, making data insights accessible to everyone in your organization, regardless of technical expertise.

## Technical Architecture

### Natural Language Processing Pipeline
Our backend implements a sophisticated NLP pipeline leveraging IBM WatsonX with the Granite-3.1-8b-instruct model. The pipeline consists of several key components:

1. Query Preprocessing
- Input validation and sanitization
- Context extraction from conversation history
- Schema metadata integration

2. NLP-to-SQL Conversion
- Semantic parsing using Granite-3.1-8b-instruct
- SQL query generation with schema validation
- Query optimization and safety checks

3. Response Processing
- Result formatting and aggregation
- Natural language response generation
- Context persistence in Redis

### Data Flow Architecture
The system implements a robust data flow process:
1. The FastAPI backend receives natural language queries via REST endpoints
2. Queries are enriched with conversation context from Redis
3. The enhanced query is processed through the WatsonX pipeline
4. Generated SQL is validated and optimized
5. Queries are executed against the PostgreSQL database
6. Results are processed and returned with both raw data and natural language insights

### Security Implementation
- Input validation and SQL injection prevention
- Query validation framework preventing destructive operations
- Role-based access control
- Data encryption in transit and at rest

### Caching and Performance
- Redis implementation for conversation history
- 24-hour context retention with automatic cleanup
- Query result caching for common requests
- Asynchronous processing for long-running queries

## API Documentation

### Endpoints

#### Natural Language Query
```python
POST /natural_language

Request Body:
{
    "query": str,          # Natural language query
    "conversation_id": str, # Optional: For context retention
    "metadata": {          # Optional: Additional context
        "schema": str,
        "filters": dict
    }
}

Response:
{
    "status": str,
    "response": {
        "natural_language": str,  # Generated response
        "sql_query": str,         # Generated SQL
        "results": dict,          # Query results
        "conversation_id": str    # For context tracking
    }
}
```

### Error Handling
The API implements comprehensive error handling:
- Input validation errors (400)
- Authentication/Authorization errors (401/403)
- Processing errors (500)
- Query timeout handling (504)

## Built With
* Frontend
  * Tailwind CSS
  * Next.js

* Backend
  * Fast API
  * Python
  * IBM Code Engine
* AI/ML
  * IBM WatsonX
  * Granite-3.1-8b-instruct Model
* Databases
  * PostgreSQL
  * Redis

## Getting Started
To get a local copy up and running, follow these simple steps.

### Prerequisites
* Python API
* PostgreSQL 14+
* Redis 6+
* IBM Cloud account with WatsonX access

### Installation
1. Clone the repository
```bash
git clone https://github.com/yourusername/knai.git
```

2. Navigate to the project directory
```bash
cd knai
```

3. Install dependencies for both frontend and backend
```bash
# Install frontend dependencies
cd frontend
npm install

# Install backend dependencies
cd ../backend
pip install -r requirements.txt
```

4. Set up environment variables
```bash
# Create .env files from examples
cp frontend/.env.example frontend/.env
cp backend/.env.example backend/.env
```

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgments
* IBM for WatsonX platform support
* The open-source community
* Our early adopters and beta testers