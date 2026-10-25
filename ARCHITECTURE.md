# Architecture Documentation

## System Overview

EnterpriseOps Copilot is a secure, grounded GenAI assistant for enterprise business operations. The architecture enforces strict separation between the LLM and business data through a controlled tool-based approach.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CLIENT LAYER                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Browser   │  │  Browser    │  │  Browser    │  │  Browser    │        │
│  │  (React)    │  │  (React)    │  │  (React)    │  │  (React)    │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼────────────────┼───────────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY (FastAPI)                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Auth      │  │Conversations│  │  Business   │  │   Health    │        │
│  │  /auth/*    │  │ /conv/*     │  │  /api/v1/*  │  │  /health    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Orchestration│  │  Business   │  │   Auth &    │  │   Audit     │        │
│  │   Service   │  │  Services   │  │   Security  │  │   Service   │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼────────────────┼───────────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DATA ACCESS LAYER                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │Repositories │  │   Tools     │  │  LLM        │  │  Migrations │        │
│  │ (SQLAlchemy)│  │ (Read-only) │  │  Provider   │  │  (Alembic)  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER (PostgreSQL)                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  users • conversations • suppliers • products • warehouses          │   │
│  │  inventory_balances • inventory_movements                           │   │
│  │  purchase_requisitions • purchase_orders • purchase_order_lines     │   │
│  │  approval_records • goods_receipts • goods_receipt_lines            │   │
│  │  supplier_invoices • supplier_invoice_lines                         │   │
│  │  audit_events                                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Chat Request Flow

```
1. User sends message via Frontend
         │
         ▼
2. API: POST /api/v1/conversations/{id}/messages
         │
         ▼
3. Auth middleware validates JWT
         │
         ▼
4. ConversationService creates user message
         │
         ▼
5. OrchestrationService.process_question()
         │
         ├──► Build system prompt + history
         │
         ├──► LLM.chat(messages, tools)
         │       │
         │       ├──► LLM returns tool_calls
         │       │
         │       ▼
         │   For each tool_call:
         │       ├──► Validate arguments against schema
         │       ├──► Check authorization (ToolContext)
         │       ├──► Execute tool (Repository query)
         │       ├──► Generate citations from results
         │       └──► Return ToolResult to LLM
         │
         ├──► LLM generates grounded response
         │
         ▼
6. Store assistant message + citations + tool_calls
         │
         ▼
7. Return ChatResponse to Frontend
         │
         ▼
8. Frontend renders message with citation badges
```

### Tool Execution Flow

```
Tool Call (from LLM)
         │
         ▼
┌──────────────────────────────────────────┐
│          ToolContext                     │
│  - db: AsyncSession                      │
│  - user_id: int                          │
│  - repositories (lazy initialized)       │
└──────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│          Tool Function                   │
│  async def search_purchase_orders(       │
│      ctx: ToolContext,                   │
│      status: str = None,                 │
│      ...                                 │
│  ) -> ToolResult                         │
└──────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│          Repository                      │
│  await ctx.procurement_repo.search_pos() │
└──────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│          Database (PostgreSQL)           │
│  SELECT * FROM purchase_orders           │
│  WHERE status = 'pending_approval'       │
│  AND user_has_access(...)                │
└──────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│          ToolResult                      │
│  - success: bool                         │
│  - data: dict                            │
│  - citations: [{"type": "purchase_order",│
│                 "id": 123,               │
│                 "reference": "PO-1001"}] │
└──────────────────────────────────────────┘
```

## Database Schema

### Core Tables

```sql
-- Users & Authorization
users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role ENUM('employee','procurement_specialist','inventory_manager','approver','administrator'),
    department VARCHAR(100),
    warehouse_id INT REFERENCES warehouses(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
)

-- Conversations
conversations (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
)

conversation_messages (
    id SERIAL PRIMARY KEY,
    conversation_id INT REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user', 'assistant', 'system', 'tool'
    content TEXT NOT NULL,
    tool_calls TEXT,            -- JSON
    tool_results TEXT,          -- JSON
    citations TEXT,             -- JSON
    created_at TIMESTAMPTZ DEFAULT now()
)

-- Suppliers
suppliers (
    id SERIAL PRIMARY KEY,
    supplier_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    address TEXT,
    status ENUM('active','inactive','on_hold') DEFAULT 'active',
    lead_time_days INT DEFAULT 0,
    payment_terms_days INT DEFAULT 30,
    currency CHAR(3) DEFAULT 'USD',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
)

-- Products & Warehouses
products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    unit_of_measure VARCHAR(20) DEFAULT 'EA',
    standard_cost NUMERIC(12,4),
    reorder_level INT DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
)

warehouses (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
)

-- Inventory
inventory_balances (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),
    warehouse_id INT REFERENCES warehouses(id),
    quantity_on_hand INT DEFAULT 0,
    reserved_quantity INT DEFAULT 0,
    last_movement_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(product_id, warehouse_id)
)

inventory_movements (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),
    warehouse_id INT REFERENCES warehouses(id),
    movement_type ENUM('receipt','issue','transfer_in','transfer_out','adjustment','reservation','release'),
    quantity INT NOT NULL,
    reference_type VARCHAR(50),
    reference_id INT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    created_by INT REFERENCES users(id)
)

-- Procurement
purchase_requisitions (
    id SERIAL PRIMARY KEY,
    requisition_number VARCHAR(50) UNIQUE NOT NULL,
    requested_by INT REFERENCES users(id),
    status ENUM('draft','submitted','approved','rejected','converted_to_po') DEFAULT 'draft',
    description TEXT,
    required_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
)

purchase_orders (
    id SERIAL PRIMARY KEY,
    po_number VARCHAR(50) UNIQUE NOT NULL,
    supplier_id INT REFERENCES suppliers(id),
    requisition_id INT REFERENCES purchase_requisitions(id),
    status ENUM('draft','pending_approval','approved','ordered','partially_received','received','cancelled') DEFAULT 'draft',
    order_date TIMESTAMPTZ DEFAULT now(),
    expected_delivery_date TIMESTAMPTZ,
    actual_delivery_date TIMESTAMPTZ,
    currency CHAR(3) DEFAULT 'USD',
    total_amount NUMERIC(14,2) DEFAULT 0,
    notes TEXT,
    created_by INT REFERENCES users(id),
    approved_by INT REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
)

purchase_order_lines (
    id SERIAL PRIMARY KEY,
    purchase_order_id INT REFERENCES purchase_orders(id) ON DELETE CASCADE,
    requisition_id INT REFERENCES purchase_requisitions(id),
    product_id INT REFERENCES products(id),
    line_number INT NOT NULL,
    quantity_ordered INT NOT NULL,
    quantity_received INT DEFAULT 0,
    unit_price NUMERIC(12,4) NOT NULL,
    currency CHAR(3) DEFAULT 'USD',
    line_total NUMERIC(14,2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(purchase_order_id, line_number)
)

approval_records (
    id SERIAL PRIMARY KEY,
    purchase_order_id INT REFERENCES purchase_orders(id) ON DELETE CASCADE,
    approver_id INT REFERENCES users(id),
    action VARCHAR(50) NOT NULL,  -- 'approved', 'rejected', 'requested_changes'
    comments TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
)

-- Receipts
goods_receipts (
    id SERIAL PRIMARY KEY,
    gr_number VARCHAR(50) UNIQUE NOT NULL,
    purchase_order_id INT REFERENCES purchase_orders(id),
    receipt_date TIMESTAMPTZ DEFAULT now(),
    warehouse_id INT REFERENCES warehouses(id),
    received_by INT REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
)

goods_receipt_lines (
    id SERIAL PRIMARY KEY,
    goods_receipt_id INT REFERENCES goods_receipts(id) ON DELETE CASCADE,
    po_line_id INT REFERENCES purchase_order_lines(id),
    product_id INT REFERENCES products(id),
    quantity_received INT NOT NULL,
    quantity_accepted INT NOT NULL,
    quantity_rejected INT DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
)

-- Invoices
supplier_invoices (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    supplier_id INT REFERENCES suppliers(id),
    purchase_order_id INT REFERENCES purchase_orders(id),
    status ENUM('draft','submitted','matched','discrepancy','approved','paid','cancelled') DEFAULT 'draft',
    invoice_date TIMESTAMPTZ NOT NULL,
    due_date TIMESTAMPTZ,
    currency CHAR(3) DEFAULT 'USD',
    total_amount NUMERIC(14,2) DEFAULT 0,
    payment_status ENUM('unpaid','partial','paid') DEFAULT 'unpaid',
    paid_amount NUMERIC(14,2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
)

supplier_invoice_lines (
    id SERIAL PRIMARY KEY,
    invoice_id INT REFERENCES supplier_invoices(id) ON DELETE CASCADE,
    po_line_id INT REFERENCES purchase_order_lines(id),
    product_id INT REFERENCES products(id),
    line_number INT NOT NULL,
    quantity_invoiced INT NOT NULL,
    unit_price NUMERIC(12,4) NOT NULL,
    currency CHAR(3) DEFAULT 'USD',
    line_total NUMERIC(14,2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
)

-- Audit
audit_events (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id INT,
    details TEXT,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT now()
)
```

### Key Relationships

```
users 1───N conversations
conversations 1───N conversation_messages

users 1───N purchase_orders (created_by)
users 1───N purchase_orders (approved_by)
users 1───N approval_records
users 1───N goods_receipts (received_by)
users 1───N inventory_movements (created_by)

suppliers 1───N purchase_orders
suppliers 1───N supplier_invoices

purchase_orders 1───N purchase_order_lines
purchase_orders 1───N goods_receipts
purchase_orders 1───N supplier_invoices
purchase_orders 1───N approval_records

purchase_order_lines 1───N goods_receipt_lines
purchase_order_lines 1───N supplier_invoice_lines

goods_receipts 1───N goods_receipt_lines

supplier_invoices 1───N supplier_invoice_lines

products 1───N inventory_balances
products 1───N inventory_movements
products 1───N purchase_order_lines
products 1───N goods_receipt_lines
products 1───N supplier_invoice_lines

warehouses 1───N inventory_balances
warehouses 1───N inventory_movements
warehouses 1───N goods_receipts
warehouses 1───N users (warehouse_id)
```

## API Boundaries

### Authentication
```
POST   /api/v1/auth/register     - Register new user
POST   /api/v1/auth/login        - Login, returns access + refresh tokens
POST   /api/v1/auth/refresh      - Refresh access token
GET    /api/v1/auth/me           - Get current user profile
```

### Conversations
```
GET    /api/v1/conversations           - List user's conversations
POST   /api/v1/conversations           - Create new conversation
GET    /api/v1/conversations/{id}      - Get conversation with messages
PATCH  /api/v1/conversations/{id}      - Update conversation title
DELETE /api/v1/conversations/{id}      - Delete conversation
POST   /api/v1/conversations/{id}/messages - Send message (triggers LLM)
```

### Suppliers
```
GET    /api/v1/suppliers               - List suppliers (paginated, filterable)
POST   /api/v1/suppliers               - Create supplier (procurement+)
GET    /api/v1/suppliers/{id}          - Get supplier details
PATCH  /api/v1/suppliers/{id}          - Update supplier (procurement+)
```

### Products & Warehouses
```
GET    /api/v1/products                - List products
POST   /api/v1/products                - Create product (catalog write)
GET    /api/v1/products/{id}           - Get product details
PATCH  /api/v1/products/{id}           - Update product (catalog write)

GET    /api/v1/warehouses              - List active warehouses
POST   /api/v1/warehouses              - Create warehouse (catalog write)
GET    /api/v1/warehouses/{id}         - Get warehouse details
```

### Inventory
```
GET    /api/v1/inventory/balances      - List inventory balances
GET    /api/v1/inventory/balances/{product_id}/{warehouse_id} - Get specific balance
GET    /api/v1/inventory/low-stock     - List products below reorder level
GET    /api/v1/inventory/movements     - List stock movements
```

### Procurement
```
GET    /api/v1/purchase-orders         - List POs (paginated, filterable)
POST   /api/v1/purchase-orders         - Create PO (procurement write)
GET    /api/v1/purchase-orders/{id}    - Get PO with lines
PATCH  /api/v1/purchase-orders/{id}    - Update PO (procurement write)
POST   /api/v1/purchase-orders/{id}/approve - Approve PO (approver+)
POST   /api/v1/purchase-orders/{id}/reject  - Reject PO (approver+)
GET    /api/v1/purchase-orders/pending-approvals - List pending
GET    /api/v1/purchase-orders/overdue - List overdue deliveries
```

### Receipts
```
GET    /api/v1/goods-receipts          - List GRs
POST   /api/v1/goods-receipts          - Create GR (inventory write)
GET    /api/v1/goods-receipts/{id}     - Get GR details
```

### Invoices
```
GET    /api/v1/supplier-invoices       - List invoices
POST   /api/v1/supplier-invoices       - Create invoice (procurement write)
GET    /api/v1/supplier-invoices/{id}  - Get invoice details
POST   /api/v1/supplier-invoices/{id}/match-po - 2-way match
POST   /api/v1/supplier-invoices/{id}/match-gr - 3-way match
```

## Security Model

### Authentication
- JWT access tokens (30 min expiry)
- JWT refresh tokens (7 day expiry)
- Bcrypt password hashing (cost factor 12)
- Tokens stored in httpOnly cookies or localStorage

### Authorization Layers
1. **Endpoint Level**: `require_permission("write:procurement")` dependencies
2. **Repository Level**: Queries filtered by user's accessible resources
3. **Tool Level**: `ToolContext` carries user_id, repositories enforce access

### Permission Matrix
| Permission | Employee | Proc. Spec. | Inv. Mgr | Approver | Admin |
|------------|----------|-------------|----------|----------|-------|
| read:own_data | ✓ | ✓ | ✓ | ✓ | ✓ |
| read:catalog | ✓ | ✓ | ✓ | ✓ | ✓ |
| read:procurement | | ✓ | | ✓ | ✓ |
| write:procurement | | ✓ | | | ✓ |
| read:suppliers | | ✓ | | | ✓ |
| read:inventory | | | ✓ | | ✓ |
| write:inventory | | | ✓ | | ✓ |
| read:approvals | | | | ✓ | ✓ |
| write:approvals | | | | ✓ | ✓ |
| * (all) | | | | | ✓ |

### Prompt Injection Defenses
- Tool allowlisting (only 15 approved tools)
- Strict JSON schema validation on all tool arguments
- Server-side authorization (LLM cannot override)
- Data/instruction separation in message roles
- Output validation (no unexpected tool calls)
- Context limiting (only relevant tool results to LLM)

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Load Balancer (nginx/ALB)              │
└────────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Frontend     │    │  Frontend     │    │  Frontend     │
│  (React)      │    │  (React)      │    │  (React)      │
│  Port 5173    │    │  Port 5173    │    │  Port 5173    │
└───────┬───────┘    └───────┬───────┘    └───────┬───────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Backend (FastAPI)                   │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐   │
│  │  Worker 1     │  │  Worker 2     │  │  Worker 3     │   │
│  │  Port 8000    │  │  Port 8000    │  │  Port 8000    │   │
│  └───────────────┘  └───────────────┘  └───────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
            ┌───────────────┐ ┌───────────────┐
            │  PostgreSQL   │ │    Redis      │
            │  Primary      │ │  (Sessions/   │
            │  (Read/Write) │ │   Cache)      │
            └───────────────┘ └───────────────┘
```

### Docker Compose Services
- **postgres**: PostgreSQL 16 with health checks
- **backend**: FastAPI with uvicorn (3 workers)
- **frontend**: Vite dev server (dev) or nginx (prod)

### Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| DATABASE_URL | Yes | PostgreSQL connection string |
| SECRET_KEY | Yes | JWT signing key (32+ chars) |
| GROQ_API_KEY | No | Groq API key (demo mode if empty) |
| DEMO_MODE | No | Force demo mode (default: true) |
| CORS_ORIGINS | Yes | Allowed frontend origins |

## Scaling Considerations

### Horizontal Scaling
- Backend: Stateless workers behind load balancer
- Frontend: Static assets served by CDN
- Database: Read replicas for query scaling
- Sessions: Redis for distributed session store

### Performance Optimizations
- Connection pooling (SQLAlchemy async pool)
- Query result caching (TanStack Query on frontend)
- Pagination on all list endpoints
- Database indexes on filter columns
- LLM response caching for repeated queries

### Monitoring
- Health endpoint: `GET /health`
- Structured logging (JSON format)
- Audit events for compliance
- LLM latency and token usage tracking