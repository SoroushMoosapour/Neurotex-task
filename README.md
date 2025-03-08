# Code Review Microservice System

This project implements a microservice-based code review system that analyzes Python functions from GitHub repositories using LLMs.

## Architecture

The system consists of three microservices:

1. **LLM Service (AI Gateway)**: Routes requests to either remote LLM APIs (OpenAI, DeepSeek) or a locally hosted LLM.
2. **Code Analysis Service**: Handles repository processing and function analysis.
3. **Local LLM Service**: Hosts a small open-source LLM locally.

## Technologies Used

- **Robyn**: Fast, async Python web framework
- **Poetry**: Dependency management
- **Pydantic**: Data validation and settings management
- **Docker**: Containerization
- **Nox**: Automation for testing and linting
- **mypy & pylint**: Type checking and code quality

## Setup and Installation

### Prerequisites

- Docker and Docker Compose
- Python 3.9+

### Running with Docker Compose

1. Clone this repository
2. Set up environment variables (or use defaults in `.env`)
3. Run the services:

```bash
docker-compose up -d
```

## API Documentation

### LLM Service

#### POST /analyze

Analyzes a Python function and provides improvement suggestions.

**Request:**

```json
{
  "function_code": "def add(a, b): return a + b"
}
```

**Response:**

```json
{
  "suggestions": [
    "Consider adding type hints.",
    "Add a docstring for better documentation."
  ]
}
```

### Code Analysis Service

#### POST /analyze/start

Starts a background job to download a GitHub repository.

**Request:**

```json
{
  "repo_url": "https://github.com/example/repo"
}
```

**Response:**

```json
{
  "job_id": "abc123"
}
```

#### POST /analyze/function

Analyzes a function from a previously downloaded repo.

**Request:**

```json
{
  "job_id": "abc123",
  "function_name": "module_name.add"
}
```

**Response:**

```json
{
  "suggestions": [
    "Consider adding type hints.",
    "Add a docstring for better documentation."
  ]
}
```

## Development

### Running Tests

```bash
nox -s test
```

### Linting and Type Checking

```bash
nox -s lint
nox -s type_check
```

## Design Choices

- **Robyn over FastAPI**: Used Robyn for its performance and async capabilities
- **Microservice Architecture**: Allows independent scaling and deployment
- **Background Processing**: Asynchronous repository processing for better user experience
- **Model Agnosticism**: LLM Service abstracts away the specific model implementation
- **Docker Containerization**: Ensures consistent environments across deployments
