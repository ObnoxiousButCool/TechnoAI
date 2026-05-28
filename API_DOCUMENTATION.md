# Complete API Documentation - Technossus Website V2 API

## 📚 Table of Contents

1. [Authentication & Users](#authentication--users)
2. [Chat & RAG](#chat--rag)
3. [Ingestion](#ingestion)
4. [Case Studies](#case-studies)
5. [System](#system)

---

## 🔐 Authentication & Users

### Authentication Endpoints (`/api/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/auth/login` | Login and get JWT token | ❌ No |
| `POST` | `/api/auth/logout` | Logout current user | ✅ Yes |
| `GET` | `/api/auth/me` | Get current user info | ✅ Yes |

### User Management Endpoints (`/api/users`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/users` | Create new user | ✅ Yes |
| `GET` | `/api/users` | List all users | ✅ Yes |
| `GET` | `/api/users/{user_id}` | Get user by ID | ✅ Yes |
| `PUT` | `/api/users/{user_id}` | Update user | ✅ Yes |
| `DELETE` | `/api/users/{user_id}` | Delete user | ✅ Yes |

**User Schema:**
```json
{
  "userId": 1,
  "firstName": "John",
  "lastName": "Doe",
  "email": "user@example.com",
  "contactNumber": "+1234567890",
  "isActive": true,
  "createdBy": 1,
  "updatedBy": 1,
  "createdOn": "2026-05-26T10:00:00Z",
  "updatedOn": "2026-05-26T10:00:00Z"
}
```

---

## 💬 Chat & RAG

### Chat Endpoints (`/chat`)

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| `POST` | `/chat` | Ask question using RAG | 20/min |
| `DELETE` | `/chat/session/{session_id}` | Clear session history | - |

**Chat Request:**
```json
{
  "question": "What services does Technossus offer?",
  "session_id": "optional-session-id"
}
```

**Chat Response:**
```json
{
  "answer": "Generated answer from RAG...",
  "sources": [
    {
      "title": "Services",
      "url": "https://..."
    }
  ],
  "session_id": "uuid",
  "follow_ups": ["Related question 1?", "Related question 2?"]
}
```

**Features:**
- Session-based conversation memory
- Intelligent intent routing (overview, contact, closure, general)
- Service-specific slug routing
- Semantic similarity search
- Score-based filtering
- Auto-generated follow-up questions

---

## 📥 Ingestion

### Ingestion Endpoints (`/ingest`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/ingest/run` | Run ingestion pipeline | ✅ Admin Key |
| `DELETE` | `/ingest/vectors` | Clear all vectors | ✅ Admin Key |

**Auth:** Requires `X-Admin-Key` header

**Response:**
```json
{
  "status": "success",
  "results": [
    {
      "source": "website",
      "chunks": 123
    }
  ]
}
```

---

## 📋 Case Studies

### Case Study Endpoints (`/api/case-studies`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/case-studies` | List published case studies | ❌ |
| `GET` | `/api/case-studies/{slug}` | Get case study by slug | ❌ |
| `POST` | `/api/case-studies` | Create case study | ❌ |
| `PUT` | `/api/case-studies/{slug}` | Update case study | ❌ |
| `DELETE` | `/api/case-studies/{slug}` | Delete case study | ❌ |
| `GET` | `/api/case-studies/admin/all` | List all (including unpublished) | ❌ |
| `POST` | `/api/case-studies/seed` | Seed case studies data | ❌ |

**Query Parameters:**
- `industry` - Filter by industry
- `service` - Filter by service
- `limit` - Results per page (default: 100, max: 500)
- `offset` - Skip N results

**Case Study Schema:**
```json
{
  "id": 1,
  "slug": "healthcare-ai-transformation",
  "tags": "AI, Healthcare",
  "industry": "Healthcare",
  "service": "AI Business Transformation",
  "title": "Healthcare AI Transformation",
  "excerpt": "Brief description...",
  "imageUrl": "/assets/...",
  "publishedDate": "2026-05-26T00:00:00Z",
  "isPublished": true,
  "content": "Full content...",
  "tagLine": "Tagline text",
  "heroImage": "/assets/hero.jpg",
  "clientName": "Hospital XYZ",
  "clientDescription": "Leading healthcare provider...",
  "challengeHeading": "The Challenge",
  "challengeBody": "Challenge description...",
  "solutionHeading": "Our Solution",
  "solutionBody": "Solution description...",
  "solutionCapabilities": ["AI", "ML", "Analytics"],
  "impactHeading": "The Impact",
  "impactDescription": "Impact summary...",
  "impactContextLabel": "Context",
  "impactContextBody": "Context details...",
  "impactCards": [
    {
      "title": "50% Reduction",
      "body": "In processing time"
    }
  ],
  "industryStats": [
    {
      "value": "70%",
      "label": "Efficiency Gain"
    }
  ],
  "relatedCaseStudies": [...]
}
```

---

## 🏥 System

### System Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |

**Response:**
```json
{
  "status": "ok"
}
```

---

## 🔑 Authentication Headers

For endpoints requiring JWT authentication:

```
Authorization: Bearer <your_jwt_token>
```

For admin endpoints (ingestion):

```
X-Admin-Key: your-admin-api-key
```

---

## 📊 Complete Endpoint Summary

### Public Endpoints (No Auth)
- ✅ `/health` - Health check
- ✅ `/api/auth/login` - Login
- ✅ `/api/case-studies*` - Case studies (read)

### Protected Endpoints (JWT Auth)
- 🔐 `/api/auth/logout` - Logout
- 🔐 `/api/auth/me` - Current user
- 🔐 `/api/users*` - User management
- 🔐 `/chat` - Chat with RAG
- 🔐 `/chat/session/{id}` - Clear session

### Admin Endpoints (API Key)
- 🔑 `/ingest/run` - Run ingestion
- 🔑 `/ingest/vectors` - Clear vectors

---

## 🌐 Base URLs

**Local Development:**
```
http://localhost:8000
```

**Interactive Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🚀 Quick Start

### 1. Login and Get Token
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

### 2. Use Token for Protected Endpoints
```bash
TOKEN="your_jwt_token_here"

curl -X GET http://localhost:8000/api/users \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Ask a Question (Chat)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question":"What services does Technossus offer?"}'
```

### 4. List Case Studies
```bash
curl -X GET "http://localhost:8000/api/case-studies?industry=Healthcare&limit=10"
```

### 5. Run Ingestion (Admin)
```bash
curl -X POST http://localhost:8000/ingest/run \
  -H "X-Admin-Key: your-admin-key"
```

---

## 📁 File Locations

- **Auth API:** [src/api/auth.py](src/api/auth.py)
- **Users API:** [src/api/users.py](src/api/users.py)
- **Chat API:** [src/api/chat.py](src/api/chat.py)
- **Ingest API:** [src/api/ingest.py](src/api/ingest.py)
- **Case Studies API:** [src/api/case_studies_new.py](src/api/case_studies_new.py)
- **Main App:** [src/main.py](src/main.py)
- **Schemas:** [src/models/schemas.py](src/models/schemas.py)
- **User Service:** [src/services/user_service.py](src/services/user_service.py)
- **Auth Service:** [src/services/auth.py](src/services/auth.py)

---

## 🔧 Configuration

See [.env](.env) for all configuration options:
- Database connection
- Ollama/LLM settings
- JWT configuration
- CORS settings
- Admin API key
- Rate limiting

---

## 📖 Additional Documentation

- **User Authentication:** See [USER_AUTH_API.md](USER_AUTH_API.md)
- **Main README:** See [README.md](README.md)
