# PostgreSQL Schema Design Skill

## Overview
This skill provides expert-level guidelines for designing PostgreSQL schemas, focusing on performance, maintainability, and data integrity.

## Naming Conventions
- **Tables**: Use `snake_case` and plural nouns (e.g., `users`, `order_items`).
- **Columns**: Use `snake_case`. Avoid generic names like `id` if possible for foreign keys (use `user_id` instead of just `id` in the `orders` table, though Django conventions usually default to `id` for primary keys).
- **Indexes**: Explicitly name indexes: `idx_<table_name>_<column_names>`.
- **Constraints**: Name constraints: `pk_<table_name>`, `fk_<table_name>_<ref_table>`, `uq_<table_name>_<column>`.

## Data Types
- **Primary Keys**: Use `BIGINT` or `UUID` for scalability.
  - Django: `BigAutoField` (default in modern Django).
  - UUID: useful for distributed systems/hiding sequential IDs.
- **Text**: Use `TEXT` instead of `VARCHAR(n)` unless you have a hard constraint. Postgres optimizes `TEXT` effectively.
- **Booleans**: Use `BOOLEAN`, not `CHAR(1)` or `INT`.
- **Timestamps**: Always use `TIMESTAMPTZ` (timestamp with time zone).
- **JSON**: Use `JSONB` for binary storage and indexing capability, not `JSON`.

## Database Design Patterns
- **Normalization**: Aim for 3NF. Denormalize only when performance benchmarks demand it.
- **Foreign Keys**: Always define foreign keys to enforce referential integrity.
- **Indexes**:
  - Index foreign keys.
  - Index columns used in `WHERE`, `ORDER BY`, `GROUP BY`.
  - Use Partial Indexes for common filters (e.g., `WHERE is_active = true`).
  - Use GIN indexes for `JSONB` and Full-Text Search (`tsvector`).

## Security & Concurrency
- **RLS (Row Level Security)**: Check if RLS is needed for multi-tenant isolation.
- **Transactions**: Keep transactions short. Avoid long-running transactions that hold locks.
- **Locking**: Be aware of lock levels (row vs table). ALTER TABLE queries can lock the whole table.

## Django Specifics
- Use `db_table` in Meta to explicitly name tables if working with legacy or specific schemas.
- Use `db_index=True` for frequently filtered fields.
- Use `unique_together` or `UniqueConstraint` in Meta.

## Documentation
- Add `COMMENT ON COLUMN` or `help_text` in Django models to document the schema logic directly in the database/code.
