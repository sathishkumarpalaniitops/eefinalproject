# GitHub Gists API

##  Overview

This project implements a lightweight HTTP API that fetches **public GitHub Gists** for a given user and returns a simplified, structured response.

Built using **FastAPI**, the application is fully tested, containerized with Docker, and designed with **SRE and DevOps best practices** in mind.

---

##  Features

* Fetch public gists for any GitHub user
* Clean and minimal JSON response
* Robust error handling (invalid user / API failures)
* Automated tests with mocking (no external dependency)
* Dockerized application (production-ready)
* Health check endpoint

---

##  Tech Stack

* Python 3
* FastAPI
* httpx (async HTTP client)
* pytest
* Docker

---

##  Project Structure

```bash
.
├── app/                # Application source code
├── tests/              # Unit tests
├── Dockerfile          # Container definition
├── requirements.txt    # Dependencies
├── README.md           # Documentation
└── .gitignore
```

---

##  Prerequisites

* Python 3.8+
* pip
* Docker (optional)

---

##  Run Locally (Recommended for Development)

### 1. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the application

```bash
uvicorn app.main:app --reload
```

###  Access API

```
http://127.0.0.1:8000/octocat
```

---

##  Run with Docker (Production-like)

### 1. Build image

```bash
docker build -t gist-api .
```

### 2. Run container

```bash
docker run -p 8080:8080 gist-api
```

###  Access API

```
http://localhost:8080/octocat
```

---

##  API Endpoints

###  GET /{username}

Fetch public gists for a GitHub user.

#### Example

```
GET /octocat
```

#### Response

```json
{
  "gists": [
    {
      "id": "123",
      "description": "Example gist",
      "url": "https://gist.github.com/..."
    }
  ]
}
```

---

###  GET /

Health check endpoint

```json
{
  "message": "API is running"
}
```

---

##  Running Tests

```bash
pytest -v
```

### ✔️ Coverage Includes:

* Successful API response
* Mocked GitHub API calls
* Error handling scenarios

---

##  Configuration

Optional `.env` file:

```bash
ENV=development
PORT=8000
```

---

##  Design Decisions

* **FastAPI** → async, high-performance API framework
* **httpx** → async HTTP calls to external services
* **Mocking in tests** → ensures reliability without external dependency
* **Docker** → consistent runtime across environments
* **Timeout handling** → avoids hanging upstream requests

---

##  Assumptions

* Only public gists are required
* No authentication required
* Simplified response is sufficient

---

##  Limitations

* No pagination support
* No caching
* No GitHub API rate limit handling
* Minimal logging

---

##  Future Improvements

* Add caching layer (Redis)
* Implement pagination
* Add structured logging
* Handle GitHub API rate limiting
* Add observability (Prometheus/Grafana)
* CI/CD pipeline (GitHub Actions)
* Kubernetes deployment

---

##  DevOps & SRE Considerations

* Containerized for reproducibility
* Health endpoint for monitoring
* Test isolation using mocks
* Ready for CI/CD integration
* Designed for scalability and resilience improvements

---

##  Author

Sathish Kumar Palani

---

## Conclusion

This project demonstrates:

* API design and development
* Dependency management
* Testability with mocking
* Containerization best practices
* Foundations of SRE-focused system design

