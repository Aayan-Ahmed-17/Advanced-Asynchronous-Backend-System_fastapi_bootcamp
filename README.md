# Advanced Asynchronous Backend System (Enterprise Core)

A high-performance, non-blocking asynchronous security and user routing engine built with **FastAPI**, **MongoDB (PyMongo Async)**, and **Redis**. This system implements modern authentication patterns with a focus on visual excellence, performance, and security.

---

## 🚀 Features

- **Asynchronous Native Architecture**: Fully non-blocking I/O using the modern PyMongo Async driver and `redis.asyncio`.
- **State-of-the-Art Authentication**:
    - Dual-Token strategy (Access & Refresh tokens) with independent secrets.
    - Real-time token blacklisting via Redis for secure logout.
    - Native `bcrypt` hashing for industry-standard security.
- **Enterprise-Ready Infrastructure**:
    - FastAPI Lifespan management for optimized connection pooling.
    - Global structured logging and CORS middleware.
    - Pydantic v2 schemas for strict data validation and contract enforcement.
- **Automated Verification**: GitHub Actions CI/CD workflow for linting and testing.

---

## 🛠️ Tech Stack

- **Core**: Python 3.12, FastAPI
- **Database**: MongoDB (Async Driver)
- **Cache**: Redis (Blacklist Layer)
- **Security**: PyJWT, Bcrypt
- **DevOps**: GitHub Actions, Pytest, HTTPX

---

## 📋 Prerequisites

- Python 3.10+
- MongoDB instance (Local or Atlas)
- Redis instance

---

## ⚙️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd "Advanced Asynchronous Backend System (Enterprise Core)"
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   MONGO_URI=mongodb://your_mongo_connection_string
   REDIS_URL=redis://localhost:6379/0
   SECRET_KEY_ACCESS=your_access_secret_key
   SECRET_KEY_REFRESH=your_refresh_secret_key
   ```

---

## 🏃 Running the Application

Start the development server with auto-reload:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

---

## 📖 API Documentation

FastAPI provides interactive documentation out of the box:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Core Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Authenticate and get Access/Refresh tokens |
| `POST` | `/auth/logout` | Revoke current session (Blacklist token) |
| `POST` | `/auth/refresh` | Rotate access tokens |

---

## 🧪 Testing

Run the automated authentication flow test to verify the system integrity:

```bash
python -m scratch.test_auth_flow
```

---

## 🏗️ Project Structure

```text
├── app/
│   ├── config/       # DB and Redis configurations
│   ├── dependencies/ # Auth and Security logic
│   ├── models/       # MongoDB Pydantic models
│   ├── routes/       # API endpoint definitions
│   ├── schemas/      # Request/Response validation schemas
│   └── main.py       # Application entry point & lifespan
├── scratch/          # Development test scripts
├── .github/          # CI/CD Workflows
└── requirements.txt  # Project dependencies
```

---

## 📄 License

This project is licensed under the MIT License.
