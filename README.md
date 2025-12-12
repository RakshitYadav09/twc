# 🚀 Multi-Tenant Organization Management API

A **production-ready FastAPI backend** for managing organizations in a multi-tenant architecture. Each organization gets its own MongoDB collection, complete with JWT authentication, secure password hashing, and async operations.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [API Endpoints](#-api-endpoints)
- [Authentication Flow](#-authentication-flow)
- [Design Decisions](#-design-decisions)
- [Project Structure](#-project-structure)

---

## ✨ Features

- ✅ **Multi-Tenant Architecture**: Each organization has its own MongoDB collection
- ✅ **JWT Authentication**: Secure token-based authentication
- ✅ **Password Security**: Bcrypt hashing for password storage
- ✅ **Async Operations**: Built with async/await for high performance
- ✅ **Clean Architecture**: Modular design with clear separation of concerns
- ✅ **Comprehensive Validation**: Pydantic models for request/response validation
- ✅ **Auto-Generated Docs**: Interactive API documentation with Swagger UI
- ✅ **Production Ready**: Error handling, logging, and CORS configuration

---

## 🏗️ Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                       CLIENT LAYER                          │
│              (Web/Mobile/API Consumers)                     │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/HTTPS Requests
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   FASTAPI APPLICATION                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              ROUTES LAYER                            │  │
│  │  • org_routes.py  (Organization endpoints)           │  │
│  │  • auth_routes.py (Authentication endpoints)         │  │
│  └───────────────┬──────────────────────────────────────┘  │
│                  │                                          │
│  ┌───────────────▼──────────────────────────────────────┐  │
│  │           MIDDLEWARE & DEPENDENCIES                  │  │
│  │  • CORS Configuration                                │  │
│  │  • JWT Token Validation                              │  │
│  │  • Request/Response Validation (Pydantic)            │  │
│  └───────────────┬──────────────────────────────────────┘  │
│                  │                                          │
│  ┌───────────────▼──────────────────────────────────────┐  │
│  │             SERVICES LAYER                           │  │
│  │  • org_service.py  (Business logic for orgs)         │  │
│  │  • auth_service.py (Authentication logic)            │  │
│  └───────────────┬──────────────────────────────────────┘  │
│                  │                                          │
│  ┌───────────────▼──────────────────────────────────────┐  │
│  │          DATABASE LAYER                              │  │
│  │  • connection.py        (Database connection)        │  │
│  │  • master_repository.py (Data access layer)          │  │
│  └───────────────┬──────────────────────────────────────┘  │
│                  │                                          │
│  ┌───────────────▼──────────────────────────────────────┐  │
│  │            UTILITIES                                 │  │
│  │  • jwt_utils.py      (Token generation/validation)   │  │
│  │  • hash_utils.py     (Password hashing)              │  │
│  │  • response_utils.py (Response formatting)           │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   MONGODB ATLAS                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         MASTER DATABASE                              │  │
│  │  • master_organizations (Org metadata)               │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      TENANT COLLECTIONS (Per Organization)           │  │
│  │  • org_alpha   (Organization "alpha" data)           │  │
│  │  • org_beta    (Organization "beta" data)            │  │
│  │  • org_gamma   (Organization "gamma" data)           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

Note: the master database in this project additionally stores the admin's bcrypt-hashed password under the `admin_hashed_password` field of the `master_organizations` document. Full admin user records are still maintained in each tenant collection; the hash in master provides a quick reference and satisfies the assignment requirement to keep admin credentials in the master metadata.

### Data Flow

1. **Client Request** → Routes receive HTTP request
2. **Validation** → Pydantic models validate request data
3. **Authentication** → JWT token validated (if required)
4. **Business Logic** → Service layer processes request
5. **Database** → Repository layer interacts with MongoDB
6. **Response** → Standardized JSON response sent to client

---

## 🛠️ Technology Stack

| Component           | Technology        | Purpose                          |
|---------------------|-------------------|----------------------------------|
| **Framework**       | FastAPI           | High-performance async web framework |
| **Database**        | MongoDB Atlas     | NoSQL document database          |
| **DB Driver**       | Motor             | Async MongoDB driver             |
| **Authentication**  | JWT (PyJWT)       | Secure token-based auth          |
| **Password Hashing**| bcrypt (passlib)  | Secure password storage          |
| **Validation**      | Pydantic          | Data validation and serialization |
| **Server**          | Uvicorn           | ASGI server                      |
| **Config**          | python-dotenv     | Environment variable management  |

---

## 📥 Installation

### Prerequisites

- Python 3.10 or higher
- MongoDB Atlas account (or local MongoDB)
- pip package manager

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd twc
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### Environment Variables

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

The `.env` file should contain your connection and secret values. For
security reasons this repository does not include real secrets. Example:

```env
# MongoDB Configuration
MONGO_URL=mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority
MASTER_DB_NAME=multi_tenant_master

# JWT Configuration
JWT_SECRET=replace_with_a_long_random_secret
JWT_ALGORITHM=HS256
TOKEN_EXPIRE_HOURS=24

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

### Configuration Details

| Variable            | Description                                    | Default Value              |
|---------------------|------------------------------------------------|----------------------------|
| `MONGO_URL`         | MongoDB connection string                      | (Your Atlas URL)           |
| `MASTER_DB_NAME`    | Name of master database for org metadata       | `multi_tenant_master`      |
| `JWT_SECRET`        | Secret key for JWT token signing               | (64-char hex string)       |
| `JWT_ALGORITHM`     | Algorithm for JWT encoding                     | `HS256`                    |
| `TOKEN_EXPIRE_HOURS`| Token expiration time in hours                 | `24`                       |
| `SERVER_HOST`       | Host address for the server                    | `0.0.0.0`                  |
| `SERVER_PORT`       | Port number for the server                     | `8000`                     |

---

## 🚀 Running the Application

### Development Mode (with auto-reload)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Alternative: Run via Python

```bash
python -m app.main
```

### Verify Server is Running

Open your browser and navigate to:

- **API Root**: http://localhost:8000/
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 📚 API Documentation

FastAPI automatically generates interactive API documentation:

### Swagger UI (Interactive)
🔗 http://localhost:8000/docs

- Try out endpoints directly in the browser
- View request/response schemas
- Test authentication

### ReDoc (Reference)
🔗 http://localhost:8000/redoc

- Clean, organized API reference
- Detailed schema documentation
- Download OpenAPI spec

---

## 🔌 API Endpoints

### Authentication Endpoints

#### 1. Admin Login
**POST** `/admin/login`

**Description**: Authenticate admin and receive JWT token

**Request Body**:
```json
{
  "email": "admin@example.com",
  "password": "securepass"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "admin_email": "admin@example.com",
  "organization_name": "alpha"
}
```

#### 2. Get Current Admin Info
**GET** `/admin/me`

**Authentication**: Required (Bearer token)

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Current admin info retrieved",
  "data": {
    "admin_id": "507f1f77bcf86cd799439011",
    "email": "admin@example.com",
    "organization_name": "alpha"
  }
}
```

---

### Organization Endpoints

#### 1. Create Organization
**POST** `/org/create`

**Description**: Create a new organization with admin user

**Request Body**:
```json
{
  "organization_name": "alpha",
  "email": "admin@example.com",
  "password": "securepass"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "message": "Organization created successfully",
  "data": {
    "organization_name": "alpha",
    "collection_name": "org_alpha",
    "admin_email": "admin@example.com",
    "admin_id": "507f1f77bcf86cd799439011",
    "created_at": "2025-12-12T10:30:00",
    "is_active": true
  }
}
```

#### 2. Get Organization
**GET** `/org/get?organization_name=alpha`

**Description**: Retrieve organization metadata by name

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Organization retrieved successfully",
  "data": {
    "organization_name": "alpha",
    "collection_name": "org_alpha",
    "admin_email": "admin@example.com",
    "created_at": "2025-12-12T10:30:00",
    "updated_at": "2025-12-12T10:30:00",
    "is_active": true
  }
}
```

#### 3. List All Organizations
**GET** `/org/list`

**Description**: Retrieve all organizations

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Retrieved 3 organization(s)",
  "data": [
    {
      "organization_name": "alpha",
      "collection_name": "org_alpha",
      "admin_email": "admin@alpha.com",
      "created_at": "2025-12-12T10:30:00",
      "is_active": true
    },
    {
      "organization_name": "beta",
      "collection_name": "org_beta",
      "admin_email": "admin@beta.com",
      "created_at": "2025-12-12T11:00:00",
      "is_active": true
    }
  ]
}
```

#### 4. Update Organization
**PUT** `/org/update`

**Authentication**: Required (Bearer token)

**Description**: Update organization name, admin email, or password

**Request Body**:
```json
{
  "old_organization_name": "alpha",
  "new_organization_name": "alpha_updated",
  "email": "newadmin@example.com",
  "password": "newsecurepass"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Organization updated successfully",
  "data": {
    "organization_name": "alpha_updated",
    "collection_name": "org_alpha_updated",
    "admin_email": "newadmin@example.com",
    "updated_at": "2025-12-12T12:00:00"
  }
}
```

#### 5. Delete Organization
**DELETE** `/org/delete`

**Authentication**: Required (Bearer token)

**Description**: Delete organization and its collection

**Request Body**:
```json
{
  "organization_name": "alpha"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Organization 'alpha' deleted successfully",
  "data": {
    "organization_name": "alpha",
    "deleted_collection": "org_alpha"
  }
}
```

---

## 🔐 Authentication Flow

### 1. Create Organization
```
POST /org/create
→ Organization "alpha" created
→ Collection "org_alpha" created
→ Admin user stored in "org_alpha"
```

### 2. Login
```
POST /admin/login
{
  "email": "admin@example.com",
  "password": "securepass"
}
→ Returns JWT token
```

### 3. Use Protected Endpoints
```
PUT /org/update
Header: Authorization: Bearer <jwt_token>
→ Token validated
→ Admin permissions checked
→ Operation performed
```

### Token Structure

JWT payload contains:
```json
{
  "admin_id": "507f1f77bcf86cd799439011",
  "email": "admin@example.com",
  "organization_name": "alpha",
  "exp": 1702393200,
  "iat": 1702306800
}
```

---

## 🤔 Design Decisions

### 1. Multi-Tenant Architecture

**Choice**: Per-tenant collections (one collection per organization)

**Pros**:
- ✅ Complete data isolation between organizations
- ✅ Easy to backup/restore individual organizations
- ✅ Simpler queries (no tenant filtering needed)
- ✅ Can apply different indexes per organization
- ✅ Easy to scale specific organizations

**Cons**:
- ⚠️ More collections in database
- ⚠️ Potential for schema drift between collections

**Alternative**: Shared collection with `tenant_id` field

**Why We Chose Per-Tenant Collections**:
- Better security through physical data separation
- Easier compliance with data residency requirements
- Simpler application logic (no tenant filtering bugs)

---

### 2. JWT Authentication

**Choice**: Stateless JWT tokens with bearer scheme

**Pros**:
- ✅ No server-side session storage needed
- ✅ Scales horizontally
- ✅ Works well with microservices
- ✅ Standard, well-supported

**Implementation Details**:
- Algorithm: HS256 (symmetric signing)
- Expiration: 24 hours (configurable)
- Payload includes: admin_id, email, organization_name

---

### 3. Password Security

**Choice**: bcrypt hashing via passlib

**Why**:
- Industry-standard for password hashing
- Automatically handles salting
- Computationally expensive (resists brute force)
- Future-proof (can upgrade algorithm)

---

### 4. Async Architecture

**Choice**: Fully async with Motor and FastAPI

**Benefits**:
- High concurrency without threading overhead
- Better resource utilization
- Non-blocking I/O operations
- Modern Python best practices

---

### 5. Clean Architecture

**Separation of Concerns**:

```
Routes → Services → Repositories → Database
```

- **Routes**: HTTP layer, validation, serialization
- **Services**: Business logic, orchestration
- **Repositories**: Data access, queries
- **Database**: Connection management

**Benefits**:
- Easy to test (mock services/repositories)
- Clear responsibilities
- Easy to modify/extend
- Better code organization

---

## 📁 Project Structure

```
c:\code\twc\
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── config/
│   │   └── settings.py            # Environment configuration
│   ├── database/
│   │   ├── connection.py          # Database connection management
│   │   └── master_repository.py   # Master DB data access layer
│   ├── models/
│   │   ├── org_models.py          # Organization Pydantic models
│   │   ├── admin_models.py        # Admin user models
│   │   └── auth_models.py         # Authentication models
│   ├── routes/
│   │   ├── org_routes.py          # Organization API endpoints
│   │   └── auth_routes.py         # Authentication endpoints
│   ├── services/
│   │   ├── org_service.py         # Organization business logic
│   │   └── auth_service.py        # Authentication business logic
│   └── utils/
│       ├── jwt_utils.py           # JWT token utilities
│       ├── hash_utils.py          # Password hashing utilities
│       └── response_utils.py      # Response formatting utilities
├── .env                           # Environment variables
├── .env.example                   # Example environment file
├── .gitignore                     # Git ignore patterns
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## 🧪 Testing the API

### Using cURL

**Create Organization**:
```bash
curl -X POST http://localhost:8000/org/create \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "alpha",
    "email": "admin@example.com",
    "password": "securepass"
  }'
```

**Login**:
```bash
curl -X POST http://localhost:8000/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "securepass"
  }'
```

**Get Organization (with token)**:
```bash
curl -X GET "http://localhost:8000/org/get?organization_name=alpha" \
  -H "Authorization: Bearer <your_token_here>"
```

---

## 🐛 Troubleshooting

### Issue: Cannot connect to MongoDB

**Solution**: 
- Verify MongoDB Atlas URL in `.env`
- Check network/firewall settings
- Ensure IP whitelist in MongoDB Atlas includes your IP

### Preparing this repository for submission

- Remove any real secrets from the workspace before publishing. This repository previously contained a `.env` file with sensitive values; that file has been removed for safety. Use `.env.example` to provide environment examples only.
- Ensure you set your production/test secrets as CI secrets in GitHub (do not commit them).
- CI is provided via GitHub Actions: see `.github/workflows/ci.yml`. It runs the simple test runner `python tests/run_tests.py` to validate the basic utils.

### Files added for reviewers

- `postman_collection.json`: Postman collection you can import to test endpoints quickly.
- `scripts/integration_test.py`: A self-contained integration script that performs create -> login -> update -> delete against a running local server.
- `scripts/test_api.sh` / `scripts/test_api.ps1`: Quick smoke test CLI scripts using `curl` / PowerShell.
- `.github/workflows/ci.yml`: CI workflow that installs dependencies and runs `tests/run_tests.py`.

### How to prepare and submit

1. Remove any remaining sensitive files (if present). The repository no longer contains `.env`.
2. Commit and push to a GitHub repository.
3. In your GitHub repo, add any required secrets (e.g., `MONGO_URL`, `JWT_SECRET`) in Settings > Secrets for actions if you later enable integration tests in CI.
4. Share the GitHub repository link with reviewers.


### Issue: Token validation fails

**Solution**:
- Check token hasn't expired (24h default)
- Verify `JWT_SECRET` matches the one used to create token
- Ensure `Authorization: Bearer <token>` header format is correct

### Issue: Import errors

**Solution**:
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check Python version is 3.10+

---

## 📝 License

This project is for educational purposes.

---

## 👨‍💻 Author

Built as a complete FastAPI backend assignment solution with production-ready architecture and best practices.

---

## 🎯 Next Steps

To extend this project, consider:

1. **Add unit tests** (pytest + pytest-asyncio)
2. **Implement refresh tokens** for better security
3. **Add role-based access control** (RBAC)
4. **Implement rate limiting** (slowapi)
5. **Add logging** (structured logging with loguru)
6. **Containerization** (Docker + Docker Compose)
7. **CI/CD pipeline** (GitHub Actions)
8. **Database migrations** (Beanie ODM)
9. **API versioning** (v1, v2 routes)
10. **Monitoring** (Prometheus + Grafana)

---

**🎉 Happy Coding!**
