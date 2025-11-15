# TSH ERP Documentation Glossary

**Version:** 1.0.0
**Last Updated:** 2025-11-15
**Purpose:** Master reference for standardized terminology across ALL TSH ERP documentation

---

## 🎯 How to Use This Glossary

**When writing ANY documentation:**
1. Use the **PREFERRED** term (first entry)
2. Avoid **DEPRECATED** alternatives
3. Follow the exact capitalization and formatting shown
4. Link to this glossary when introducing technical terms

---

## 📚 Product & Integration Names

### Zoho Products

**Zoho Books**
- **Preferred:** `Zoho Books` (two words, both capitalized)
- **Use when:** Referring to the accounting/financial platform
- **Deprecated:** `ZohoBooks`, `zoho books`, `zoho-books`, `Books` (without Zoho prefix)
- **Example:** "TDS Core syncs data from Zoho Books and Zoho Inventory."

**Zoho Inventory**
- **Preferred:** `Zoho Inventory` (two words, both capitalized)
- **Use when:** Referring to the inventory/products platform
- **Deprecated:** `ZohoInventory`, `zoho inventory`, `zoho-inventory`, `Inventory` (without Zoho prefix)
- **Example:** "Product data comes from Zoho Inventory via TDS Core."

**Zoho Organization ID**
- **Preferred:** `Zoho Organization ID` or `Organization ID: 748369814`
- **Deprecated:** `org_id`, `zoho_org`, `organization id`
- **Example:** "Both Zoho Books and Zoho Inventory use Organization ID 748369814."

### TSH ERP Components

**TDS Core**
- **Preferred:** `TDS Core` (two words, both capitalized, no hyphen)
- **Full Name:** TSH Data Sync Core
- **Use when:** Referring to the Zoho sync orchestration system
- **Deprecated:** `TDS`, `tds-core`, `tds_core`, `TdsCore`, `TDS-Core`
- **Code reference:** `app/tds/` directory
- **Example:** "TDS Core orchestrates ALL synchronization with Zoho Books and Zoho Inventory."

**TSH NeuroLink**
- **Preferred:** `TSH NeuroLink` (capitalized, no hyphen, no space in NeuroLink)
- **Use when:** Referring to the unified notification/communication system
- **Deprecated:** `NeuroLink`, `Neuro-Link`, `neurolink`, `TSH Neuro-Link`
- **Code reference:** `app/neurolink/` directory
- **Example:** "TSH NeuroLink handles ALL notifications and internal communications."

**BFF (Backend-for-Frontend)**
- **Preferred:** `BFF` as acronym, or `Backend-for-Frontend` spelled out
- **Use when:** Referring to mobile-optimized API endpoints
- **Deprecated:** `backend for frontend`, `Backend For Frontend`, `BackendForFrontend`
- **Code reference:** `app/bff/` directory
- **Example:** "Mobile apps consume the BFF (Backend-for-Frontend) endpoints."

**TSH ERP Ecosystem**
- **Preferred:** `TSH ERP Ecosystem` (full project name)
- **Short form:** `TSH ERP` (when context is clear)
- **Deprecated:** `TSH-ERP`, `tsh_erp`, `TSH erp`, `The ERP`, `The System`
- **Example:** "The TSH ERP Ecosystem includes 8 Flutter mobile apps."

### Technology Stack

**FastAPI**
- **Preferred:** `FastAPI` (one word, camelCase)
- **Deprecated:** `Fast API`, `fast-api`, `FASTAPI`
- **Example:** "The backend is built with FastAPI and PostgreSQL."

**PostgreSQL**
- **Preferred:** `PostgreSQL` (one word, camelCase)
- **Acceptable:** `Postgres` (informal, in casual docs)
- **Deprecated:** `PostgresSQL`, `postgres-sql`, `POSTGRESQL`
- **Example:** "Data is stored in PostgreSQL 12+ database."

**SQLAlchemy**
- **Preferred:** `SQLAlchemy` (one word, camelCase)
- **Deprecated:** `SQL Alchemy`, `sqlalchemy` (unless in code)
- **Example:** "Database models use SQLAlchemy ORM."

**Flutter**
- **Preferred:** `Flutter` (capitalized)
- **Deprecated:** `flutter` (unless in code/commands)
- **Example:** "All 8 mobile apps are built with Flutter 3.0+."

**React**
- **Preferred:** `React` (capitalized)
- **Deprecated:** `react` (unless in code/imports), `ReactJS`, `React.js`
- **Example:** "The ERP Admin dashboard uses React 18 with TypeScript."

### Cloud & Infrastructure

**AWS S3**
- **Preferred:** `AWS S3` (both acronyms capitalized)
- **Bucket name:** `tsh-erp-backups` (lowercase with hyphens)
- **Region:** `eu-north-1` (lowercase)
- **Deprecated:** `Amazon S3`, `s3`, `S3`, `AWS-S3`
- **Example:** "Daily backups are stored in AWS S3 bucket tsh-erp-backups (eu-north-1)."

**GitHub Actions**
- **Preferred:** `GitHub Actions` (both capitalized)
- **Deprecated:** `Github Actions`, `github actions`, `GH Actions`
- **Example:** "Deployments are automated via GitHub Actions."

**Docker**
- **Preferred:** `Docker` (capitalized)
- **Deprecated:** `docker` (unless in commands)
- **Example:** "Services run in Docker containers orchestrated by Docker Compose."

**Nginx**
- **Preferred:** `Nginx` (capitalized)
- **Deprecated:** `nginx` (unless in config files), `NGINX`
- **Example:** "Nginx serves as reverse proxy for all web services."

---

## 🏗️ Architecture & Patterns

### Authorization Framework

**RBAC (Role-Based Access Control)**
- **Preferred:** `RBAC` as acronym, or `Role-Based Access Control` spelled out
- **Deprecated:** `role based access control`, `Role-based Access Control`
- **Example:** "The authorization framework uses RBAC (Role-Based Access Control)."

**ABAC (Attribute-Based Access Control)**
- **Preferred:** `ABAC` as acronym, or `Attribute-Based Access Control` spelled out
- **Deprecated:** `attribute based access control`, `Attribute-based Access Control`
- **Example:** "ABAC (Attribute-Based Access Control) provides fine-grained permissions."

**RLS (Row-Level Security)**
- **Preferred:** `RLS` as acronym, or `Row-Level Security` spelled out
- **Deprecated:** `row level security`, `Row-level Security`
- **Example:** "RLS (Row-Level Security) filters database queries by user access."

**Hybrid Authorization**
- **Preferred:** `Hybrid Authorization: RBAC + ABAC + RLS`
- **Deprecated:** `Mixed authorization`, `Combined auth`, `Multi-layer auth`
- **Example:** "TSH ERP uses Hybrid Authorization combining RBAC, ABAC, and RLS."

### Development Patterns

**ORM (Object-Relational Mapping)**
- **Preferred:** `ORM` as acronym, or `Object-Relational Mapping` spelled out
- **Deprecated:** `object relational mapping`, `Object-relational Mapping`
- **Example:** "SQLAlchemy provides the ORM (Object-Relational Mapping) layer."

**JWT (JSON Web Token)**
- **Preferred:** `JWT` as acronym, or `JSON Web Token` spelled out
- **Deprecated:** `json web token`, `Json Web Token`, `jwt`
- **Example:** "Authentication uses JWT (JSON Web Token) tokens."

**RTL (Right-to-Left)**
- **Preferred:** `RTL` as acronym, or `Right-to-Left` spelled out
- **Use when:** Referring to Arabic text direction
- **Deprecated:** `right to left`, `right-to-left`
- **Example:** "All UI components support RTL (Right-to-Left) layout for Arabic."

---

## 🌍 Business & Domain Terms

### User Roles

**Wholesale Client**
- **Preferred:** `wholesale client` (lowercase unless starting sentence)
- **Plural:** `wholesale clients`
- **Deprecated:** `Wholesale Client`, `b2b client`, `B2B customer`
- **Count:** 500+ active
- **Example:** "Wholesale clients can place bulk orders with credit terms."

**Retail Customer**
- **Preferred:** `retail customer` (lowercase unless starting sentence)
- **Deprecated:** `Retail Customer`, `b2c customer`, `consumer` (use consumer app context)
- **Example:** "Retail customers pay cash at point of sale."

**Partner Salesman**
- **Preferred:** `partner salesman` (lowercase, singular)
- **Plural:** `partner salesmen` (NOT salespeople)
- **Deprecated:** `Partner Salesman`, `partner salesperson`, `affiliate`
- **Count:** 100+ active
- **Example:** "Partner salesmen earn commission on social media sales."

**Travel Salesperson**
- **Preferred:** `travel salesperson` (lowercase, singular)
- **Plural:** `travel salespersons` or `travel sales team`
- **Deprecated:** `Travel Salesperson`, `field sales`, `mobile sales`
- **Count:** 12 active handling $35K USD weekly
- **Example:** "Travel salespersons track GPS locations during field visits."

### Business Operations

**Credit Limit**
- **Preferred:** `credit limit` (lowercase unless starting sentence)
- **Deprecated:** `Credit Limit`, `credit-limit`
- **Example:** "Wholesale clients have individual credit limits enforced at order placement."

**Stock Quantity**
- **Preferred:** `stock quantity` or `inventory level`
- **Deprecated:** `stock qty`, `Stock Quantity`, `quantity in stock`
- **Example:** "Stock quantity is synced from Zoho Inventory in real-time."

**Sales Order**
- **Preferred:** `sales order` (lowercase unless starting sentence)
- **Deprecated:** `Sales Order`, `salesorder` (unless in code/API)
- **Example:** "Sales orders sync to both Zoho Books and Zoho Inventory."

**Purchase Order**
- **Preferred:** `purchase order` (lowercase unless starting sentence)
- **Deprecated:** `Purchase Order`, `purchaseorder` (unless in code/API)
- **Example:** "Purchase orders track China imports and local vendor purchases."

---

## 🔄 Migration & Sync

### Zoho Migration Phases

**Phase 1: One-Directional Sync**
- **Preferred:** `Phase 1` or `Zoho Migration Phase 1`
- **Status:** READ-ONLY from Zoho
- **Deprecated:** `phase 1`, `Phase One`, `P1`
- **Example:** "Phase 1 establishes one-directional sync from Zoho to TSH ERP."

**Phase 2: Two-Directional Sync**
- **Preferred:** `Phase 2` or `Zoho Migration Phase 2`
- **Status:** Bidirectional sync testing
- **Deprecated:** `phase 2`, `Phase Two`, `P2`
- **Example:** "Phase 2 enables writing back to Zoho for testing."

**Phase 3: Gradual TSH ERP Dependence**
- **Preferred:** `Phase 3` or `Zoho Migration Phase 3`
- **Deprecated:** `phase 3`, `Phase Three`, `P3`
- **Example:** "Phase 3 shifts primary operations to TSH ERP."

**Phase 4: Complete Independence**
- **Preferred:** `Phase 4` or `Zoho Migration Phase 4`
- **Goal:** Cut Zoho subscriptions
- **Deprecated:** `phase 4`, `Phase Four`, `P4`, `Final Phase`
- **Example:** "Phase 4 achieves complete independence from Zoho products."

### Sync Operations

**Sync Orchestration**
- **Preferred:** `sync orchestration` (lowercase)
- **Deprecated:** `Sync Orchestration`, `synchronization orchestration`
- **Example:** "TDS Core provides sync orchestration for all Zoho operations."

**One-Directional Sync**
- **Preferred:** `one-directional sync` (hyphenated)
- **Deprecated:** `one directional sync`, `uni-directional`, `one-way sync`
- **Example:** "Phase 1 uses one-directional sync from Zoho to TSH ERP."

**Two-Directional Sync**
- **Preferred:** `two-directional sync` or `bidirectional sync`
- **Deprecated:** `two directional sync`, `bi-directional`, `two-way sync`
- **Example:** "Phase 2 tests two-directional sync capabilities."

**Real-Time Sync**
- **Preferred:** `real-time sync` (hyphenated as adjective)
- **Deprecated:** `real time sync`, `realtime sync`, `RT sync`
- **Example:** "Stock levels use real-time sync with <30 second latency."

---

## 💻 Technical Conventions

### API & Endpoints

**API Endpoint**
- **Preferred:** `API endpoint` (two words)
- **Deprecated:** `api endpoint`, `API-endpoint`, `endpoint` (without API)
- **Example:** "The `/api/v1/products` API endpoint supports pagination."

**REST API**
- **Preferred:** `REST API` (both capitalized)
- **Deprecated:** `Rest API`, `rest api`, `RESTful API` (unless specifically discussing RESTful principles)
- **Example:** "The backend exposes a REST API for all client applications."

**Health Check**
- **Preferred:** `health check` (two words, lowercase)
- **Endpoint:** `/health`
- **Deprecated:** `healthcheck`, `Health Check`, `health-check`
- **Example:** "Monitor the health check endpoint at `/health`."

### Database Terms

**Primary Key**
- **Preferred:** `primary key` (lowercase unless starting sentence)
- **Deprecated:** `Primary Key`, `primary-key`, `PK`
- **Example:** "Each table uses an integer primary key named `id`."

**Foreign Key**
- **Preferred:** `foreign key` (lowercase unless starting sentence)
- **Deprecated:** `Foreign Key`, `foreign-key`, `FK`
- **Example:** "Always index foreign keys for query performance."

**Database Migration**
- **Preferred:** `database migration` or `schema migration`
- **Tool:** Alembic
- **Deprecated:** `migration`, `db migration`, `Migration`
- **Example:** "Use Alembic for all database migrations."

### Code Patterns

**Service Layer**
- **Preferred:** `service layer` (lowercase)
- **Deprecated:** `Service Layer`, `service-layer`, `business logic layer`
- **Example:** "Business logic resides in the service layer, not routes."

**Pydantic Schema**
- **Preferred:** `Pydantic schema` (capitalize Pydantic)
- **Deprecated:** `pydantic schema`, `Pydantic Schema`, `validation schema`
- **Example:** "All input validation uses Pydantic schemas."

**SQLAlchemy Model**
- **Preferred:** `SQLAlchemy model` (capitalize SQLAlchemy)
- **Deprecated:** `sqlalchemy model`, `SQL Alchemy model`, `database model`
- **Example:** "Define SQLAlchemy models in the `app/models/` directory."

---

## 🌐 Internationalization

### Language Terms

**Arabic**
- **Preferred:** `Arabic` (capitalized)
- **Field suffix:** `_ar` (e.g., `name_ar`, `description_ar`)
- **Deprecated:** `arabic`, `AR`, `ara`
- **Example:** "All user-facing models include Arabic fields (`name_ar`, `description_ar`)."

**English**
- **Preferred:** `English` (capitalized)
- **Field:** `name` (no suffix for English)
- **Deprecated:** `english`, `EN`, `eng`
- **Example:** "English is the secondary language; Arabic is primary."

**RTL Layout**
- **Preferred:** `RTL layout` or `Right-to-Left layout`
- **Deprecated:** `rtl layout`, `right to left layout`
- **Example:** "All UI components support RTL layout for Arabic text."

**Bilingual**
- **Preferred:** `bilingual` (lowercase unless starting sentence)
- **Deprecated:** `bi-lingual`, `Bilingual`, `dual-language`
- **Example:** "The system is fully bilingual (Arabic and English)."

---

## 📦 Deployment & Environment

### Environments

**Production Environment**
- **Preferred:** `production` or `production environment`
- **Server:** 167.71.39.50 (user: root)
- **Branch:** `main`
- **URLs:** `https://erp.tsh.sale`, `https://consumer.tsh.sale`
- **Deprecated:** `prod`, `Production`, `PROD`
- **Example:** "Deploy to production after thorough staging verification."

**Staging Environment**
- **Preferred:** `staging` or `staging environment`
- **Server:** 167.71.58.65 (user: khaleel)
- **Branch:** `develop`
- **URLs:** `https://staging.erp.tsh.sale`
- **Deprecated:** `stg`, `Staging`, `STAGING`, `stage`
- **Example:** "Test all features on staging before creating production PR."

**Development Environment**
- **Preferred:** `development` or `local development`
- **Deprecated:** `dev`, `Development`, `DEV`, `local`
- **Example:** "Run the development environment using Docker Compose."

### Deployment Terms

**Blue-Green Deployment**
- **Preferred:** `blue-green deployment` (hyphenated, lowercase)
- **Deprecated:** `blue green deployment`, `Blue-Green Deployment`, `bluegreen`
- **Example:** "Use blue-green deployment for zero-downtime production updates."

**Zero-Downtime Deployment**
- **Preferred:** `zero-downtime deployment` (hyphenated, lowercase)
- **Deprecated:** `zero downtime deployment`, `Zero-Downtime`, `ZDD`
- **Example:** "Zero-downtime deployment is required when TSH ERP becomes primary system."

**Continuous Integration/Continuous Deployment (CI/CD)**
- **Preferred:** `CI/CD` as acronym
- **Spelled out:** `Continuous Integration/Continuous Deployment`
- **Deprecated:** `ci/cd`, `CI-CD`, `continuous integration`
- **Example:** "GitHub Actions provides our CI/CD pipeline."

---

## 📊 Metrics & Scale

### Pagination

**Pagination**
- **Preferred:** `pagination` (lowercase)
- **Default:** 100 records per page
- **Threshold:** Paginate when > 100 records
- **Deprecated:** `Pagination`, `paging`
- **Example:** "Implement pagination for all lists exceeding 100 records."

**Page Size**
- **Preferred:** `page size` (two words)
- **Parameter:** `per_page` or `limit`
- **Deprecated:** `pagesize`, `page-size`, `Page Size`
- **Example:** "Default page size is 100 records."

### Performance

**Response Time**
- **Preferred:** `response time` (two words, lowercase)
- **Target:** < 500ms for critical operations
- **Deprecated:** `responsetime`, `response-time`, `Response Time`
- **Example:** "API response time must be under 500ms."

**Latency**
- **Preferred:** `latency` (lowercase)
- **Deprecated:** `Latency`, `lag`, `delay`
- **Example:** "Sync latency must be under 30 seconds."

---

## 🔒 Security Terms

### Authentication

**JWT Token**
- **Preferred:** `JWT token` or `JWT`
- **Deprecated:** `jwt token`, `JSON Web Token token` (redundant)
- **Example:** "Authentication requires a valid JWT token in the Authorization header."

**Access Token**
- **Preferred:** `access token` (two words, lowercase)
- **Deprecated:** `accesstoken`, `access-token`, `Access Token`
- **Example:** "Access tokens expire after 24 hours."

**Refresh Token**
- **Preferred:** `refresh token` (two words, lowercase)
- **Deprecated:** `refreshtoken`, `refresh-token`, `Refresh Token`
- **Example:** "Use refresh tokens to obtain new access tokens."

### Authorization

**Permission**
- **Preferred:** `permission` (lowercase unless starting sentence)
- **Deprecated:** `Permission`, `perms`, `access right`
- **Example:** "Check user permissions before sensitive operations."

**Role**
- **Preferred:** `role` (lowercase unless starting sentence)
- **Deprecated:** `Role`, `user role`
- **Example:** "The admin role has elevated privileges."

---

## 📝 Documentation Standards

### File Naming

**README Files**
- **Preferred:** `README.md` (all caps with .md extension)
- **Deprecated:** `readme.md`, `ReadMe.md`, `Readme.MD`
- **Example:** "Each module includes a README.md file."

**Markdown Files**
- **Preferred:** `UPPERCASE_WITH_UNDERSCORES.md` for documentation
- **Lowercase:** `kebab-case.md` for code-related docs
- **Deprecated:** `mixedCase.md`, `random_Case.md`
- **Example:** `PROJECT_VISION.md`, `api-reference.md`

### Headers

**Headers Level 1**
- **Format:** `# Title` (single #, space, capitalized title)
- **Use:** Only once per file (document title)
- **Example:** `# TSH ERP Documentation Glossary`

**Headers Level 2**
- **Format:** `## Section Title` (double ##, space, capitalized title)
- **Use:** Major sections
- **Example:** `## 🎯 How to Use This Glossary`

**Headers Level 3**
- **Format:** `### Subsection Title` (triple ###, space)
- **Use:** Subsections
- **Example:** `### Zoho Products`

**Headers Level 4+**
- **Format:** `#### Detail Title` (use sparingly)
- **Use:** Fine-grained details
- **Example:** `#### Implementation Notes`

---

## 🎓 Usage Guidelines

### When to Use This Glossary

**ALWAYS refer to this glossary when:**
- Writing new documentation
- Updating existing documentation
- Reviewing pull requests with docs changes
- Creating presentations or reports
- Communicating with external stakeholders

**Update this glossary when:**
- Adding new technical components
- Introducing new business terminology
- Changing official product names
- Discovering widely-used inconsistent terms

### Enforcement

**Required:**
- All new documentation MUST use preferred terms
- PR reviews SHOULD check terminology consistency
- Claude Code MUST use this glossary for all outputs

**Recommended:**
- Gradually update existing docs to preferred terms
- Link to this glossary from other documentation
- Train new team members on terminology standards

### Exceptions

**Acceptable variations:**
- **Code:** Variable/function names may differ (e.g., `zoho_books_id`, `tds_core_service`)
- **URLs:** Domain names are fixed (e.g., `tds.tsh.sale`)
- **File paths:** Follow filesystem conventions (e.g., `app/tds/`, `zoho_inventory.py`)
- **Historical:** Don't change old commit messages or changelogs

**Context-dependent:**
- **Casual conversation:** "TDS" instead of "TDS Core" is acceptable
- **UI labels:** May use shorter forms for space constraints
- **Error messages:** Clarity over strict terminology

---

## 📞 Questions or Additions

**To propose new terms or changes:**
1. Check if term already exists in glossary
2. Verify term is used in ≥3 documentation files
3. Propose preferred format with justification
4. Submit PR updating this file
5. Get approval from project owner

**Glossary maintainer:** Khaleel Al-Mulla
**Last reviewed:** 2025-11-15
**Next review:** 2025-12-15

---

**END OF GLOSSARY**

*This glossary is the authoritative source for TSH ERP terminology. When in doubt, consult this file.*
