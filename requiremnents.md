# **Interview Assessment**

## **Introduction**

This exercise will evaluate your skills in microservice design, FastAPI, Docker, and LLM integration. The task is expected to take **a maximum of 4 hours**.

## **Objective**

Your goal is to build a **microservice-based code review system** that analyzes Python functions from a GitHub repository. The system consists of two microservices:

1. **LLM Service (AI Gateway)**

   - Acts as a gateway to either:
     - A remote LLM (e.g., OpenAI, DeepSeek)
     - A locally hosted LLM using
   - The model to use is determined via an **environment variable**.
   - Exposes an API for function analysis.

2. **Code Analysis Service**
   - Handles repository processing.
   - Provides endpoints for submitting repos and requesting function analysis.
   - Manages background jobs for downloading repos.
   - Calls the **LLM Service** using the OpenAI Python package, remaining model-agnostic.

---

## **Service 0: Open source LLM hosting**

Hosts a small LLM locally (e.g Qwen or Llama family below 1.5B params).

## **Service 1: LLM Service (AI Gateway)**

### **Description**

This service routes requests to either a remote LLM API (like OpenAI, Deepseek) or a locally hosted LLM, based on an **environment variable** (`LLM_PROVIDER`).

### **API Endpoints**

#### `POST /analyze`

- **Input:**
  ```json
  {
    "function_code": "def add(a, b): return a + b"
  }
  ```
- **Output:**
  ```json
  {
    "suggestions": [
      "Consider adding type hints.",
      "Add a docstring for better documentation."
    ]
  }
  ```

### **Implementation Notes**

- If `LLM_PROVIDER=openai`, forward requests to OpenAI’s API.
- If `LLM_PROVIDER=deepseek`, forward requests to Deepseek’s API.
- If `LLM_PROVIDER=local`, query the locally hosted model.
- The response should be in OpenAI API format to maintain compatibility with the **Code Analysis Service**.

---

## **Service 2: Code Analysis Service**

### **Description**

Handles repository processing and function analysis, communicating with the **LLM Service**.

### **API Endpoints**

#### `POST /analyze/start`

- **Description:** Starts a **background** job to download a GitHub repository.
- **Input:**
  ```json
  {
    "repo_url": "https://github.com/example/repo"
  }
  ```
- **Output:**
  ```json
  {
    "job_id": "abc123"
  }
  ```
- **Implementation:**
  - Downloads the repo **asynchronously**.
  - Saves a `job_id` for later references to the task and repo.
  - Returns the `job_id`.

#### `POST /analyze/function`

- **Description:** Analyzes a function from a previously downloaded repo.
- **Input:**
  ```json
  {
    "job_id": "abc123",
    "function_name": "module_name.add"
  }
  ```
- **Output:**
  ```json
  {
    "suggestions": [
      "Consider adding type hints.",
      "Add a docstring for better documentation."
    ]
  }
  ```
- **Implementation:**
  - Extracts the given function code from the repo.
  - Sends it to the **LLM Service** via the OpenAI Python package.

---

## **Submission Instructions**

- Implement both services and ensure they can communicate.
- Make sure you stick with the signitiure of the endpoints you are provided with. We will test services with a pre-implemented script.
- Provide a **`README.md`** with:
  - Instructions on how to run the services.
  - Example API calls and responses.
  - Explain you technology and design choices.
- Containerize both services using Docker.
- Submit your code in a git repo.

## Would be nice to see:

- Unit tests (for at least parts of your code) and running scripts for tests
- Use of `poetry` package management
- Use of `pydantic` for handeling settings and domain objects
- Your code complies with style and type checkers (e.g. `pylint`, `mypy`)
- Using `nox` to automate your scripts.
