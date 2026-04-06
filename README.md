Finance Dashboard Backend API
A robust, role-based backend system for managing financial records, built with FastAPI, PostgreSQL (Neon), and SQLAlchemy. This system provides secure data management, real-time financial summaries, and granular access control.

🚀 Features
Role-Based Access Control (RBAC): Three distinct roles (Admin, Analyst, Viewer) with specific permissions.

JWT Authentication: Secure token-based authentication using OAuth2 and bcrypt password hashing.

Financial Record Management: Full CRUD operations for income and expense entries with data validation.

Dashboard Summary API: High-performance data aggregation (Total Income/Expense, Net Balance, and Category-wise breakdown) performed at the database level.

Persistent Storage: Integrated with Neon Serverless Postgres for reliable data persistence.

Automated Documentation: Interactive API exploration via Swagger UI (OpenAPI).

Tech Stack
Framework: FastAPI

Database: PostgreSQL (Neon)

ORM: SQLAlchemy

Validation: Pydantic

Security: Passlib (bcrypt), Python-Jose (JWT)

Environment: Python 3.10+

Design Assumptions & Trade-offs
Database Choice: Used Neon Postgres for serverless scalability and to demonstrate proficiency with cloud-hosted relational databases.

Financial Precision: Used Numeric(10, 2) (Decimal) for all currency fields to avoid floating-point arithmetic errors common in financial applications.

Security: Implemented OAuth2PasswordBearer to allow the Swagger UI to handle token-based authentication directly, making it easier for reviewers to test the API.

Performance: Summary calculations (SUM, GROUP BY) are handled via SQL aggregations rather than Python loops to ensure the backend scales efficiently with large datasets.