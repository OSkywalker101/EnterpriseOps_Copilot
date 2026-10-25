# EnterpriseOps Copilot

A secure, grounded GenAI assistant for enterprise business operations (procurement, inventory, invoices, suppliers).

## Features

- **Chat Interface**: Natural language queries about business data with source citations
- **Procurement Dashboard**: Pending approvals, overdue deliveries, invoice discrepancies
- **Inventory Dashboard**: Low stock alerts, stock movements, warehouse views
- **Supplier Management**: CRUD operations, delivery performance tracking
- **Invoice Matching**: 2-way and 3-way matching with discrepancy detection
- **Role-Based Access Control**: Employee, Procurement Specialist, Inventory Manager, Approver, Administrator
- **Audit Logging**: All actions tracked for compliance
- **Demo Mode**: Works without external API keys

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, TanStack Query, React Router
- **Backend**: FastAPI, Python 3.12, SQLAlchemy 2.0, Alembic, Pydantic 2
- **Database**: PostgreSQL 16
- **AI**: Groq API (Llama 3.1 70B) with provider abstraction
- **Auth**: JWT with refresh tokens, bcrypt password hashing
- **Testing**: Pytest, httpx
- **CI/CD**: GitHub Actions, Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OR: Python 3.12+, Node.js 20+, PostgreSQL 16+

### Using Docker Compose (Recommended)

```bash
# Copy environment template
cp backend/.env.example backend/.env

# Start all services
docker compose up -d

# Run database migrations
docker compose exec backend alembic upgrade head

# Seed demo data
docker compose exec backend python scripts/seed.py
```

### Manual Setup

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Access the Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Demo Accounts

| Email | Password | Role |
|-------|----------|------|
| admin@enterpriseops.com | admin123 | Administrator |
| procurement@enterpriseops.com | proc123 | Procurement Specialist |
| inventory@enterpriseops.com | inv123 | Inventory Manager |
| approver@enterpriseops.com | appr123 | Approver |
| employee@enterpriseops.com | emp123 | Employee |

## Example Queries

Try these in the chat interface:

- "Which purchase orders are awaiting approval?"
- "Show me overdue deliveries"
- "What products are below reorder level?"
- "Check invoice INV-2002 for discrepancies"
- "How is supplier SUP-001 performing?"
- "Summarize outstanding procurement issues"
- "What is the available stock for SKU-104?"

## Project Structure

```
enterpriseops/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── core/            # Config, security, audit
│   │   ├── db/              # Database session, base
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── repositories/    # Data access layer
│   │   ├── services/        # Business logic
│   │   ├── tools/           # LLM-approved tools
│   │   └── main.py          # FastAPI app
│   ├── alembic/             # Migrations
│   ├── scripts/             # Seed data
│   └── tests/               # Pytest tests
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom hooks
│   │   ├── services/        # API client
│   │   ├── types/           # TypeScript types
│   │   └── utils/           # Utilities
│   └── ...
├── docker-compose.yml
└── README.md
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for system diagram, data flow, and database relationships.

## Security

- All database access through validated backend functions (no direct LLM-to-DB)
- Role-based and resource-level authorization on every endpoint
- Prompt injection defenses: tool allowlisting, strict schemas, output validation
- JWT authentication with secure refresh token rotation
- Audit logging for all sensitive operations
- No secrets in code - all via environment variables

## Evaluation

Run the evaluation suite:

```bash
cd backend
pytest tests/ -v -k "eval"  # Evaluation tests
```

## License

MIT License - See LICENSE file for details.