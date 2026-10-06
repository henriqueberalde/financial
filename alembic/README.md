Generic single-database configuration. The database URL comes from `DATABASE_URL` (`.env`).
### Create a Revision
* ```alembic revision -m "some description"```

### Upgrade / Downgrade migrations
* ```alembic upgrade head```
* ```alembic downgrade -1```

To run against another database, override the variable: ```DATABASE_URL=<url> alembic upgrade head```
