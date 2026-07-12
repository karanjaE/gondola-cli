# Gondola project templates

The CLI renders Jinja templates under `gondola/templates/`:

- **`postgres/`** — default layout when `gondola create project … --db postgresql` (async Postgres, `api/`, `db/migrations/`, header-based API versioning).
- **`legacy/`** — SQLite/MySQL projects until those paths are modernized.

The **`examples/example_app/`** directory is a non-shipped reference app aligned with the Postgres template (update the Jinja trees when you change the example).
