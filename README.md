# partner-scout

AI-powered service for monitoring consulting firm partners.

## Setup

```shell
cp src/.env.example src/.env
make install
make pre-commit.install
docker volume create db_data
make compose.deps.dev
make migrate
make createsuperuser
make run
```

## URLs

- Admin: http://localhost:8000/admin/
- Swagger: http://localhost:8000/api/docs/
- OpenAPI JSON: http://localhost:8000/api/schema.json
